"""DeepAI chat wrapper for LangChain."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncIterator, Iterator, Mapping, Sequence
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    cast,
)

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import (
    BaseChatModel,
    agenerate_from_stream,
    generate_from_stream,
)
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.utils import get_pydantic_field_names
from langchain_core.utils.utils import _build_model_kwargs, secret_from_env
from pydantic import ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self

# Import DeepAI functionality
try:
    import requests
    import json
except ImportError as e:
    raise ImportError(
        "Could not import required packages. "
        "Please install them with `pip install requests`."
    ) from e

from ..core.authentication import check_api_key, get_auth_headers
from ..core.providers import get_models, get_chat_styles, validate_model, validate_chat_style, normalize_chat_style
from ..core.utils import (
    format_messages_for_deepai,
    parse_deepai_response,
    validate_message_format,
    create_request_id,
    get_current_timestamp,
    log_api_call
)

logger = logging.getLogger(__name__)


def _convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain message to a dictionary for DeepAI API.

    Args:
        message: The LangChain message.

    Returns:
        The message dictionary.
    """
    content = message.content
    
    # Handle different message types
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, SystemMessage):
        role = "system"
    elif isinstance(message, ChatMessage):
        role = message.role
    else:
        role = "user"
    
    # Handle multimodal content if needed
    if isinstance(content, list):
        # For now, concatenate text parts for DeepAI
        text_content = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_content += item.get("text", "")
            elif isinstance(item, str):
                text_content += item
        content = text_content
    
    return {
        "role": role,
        "content": str(content)
    }


def _convert_dict_to_message(message_dict: dict) -> BaseMessage:
    """Convert a dictionary to a LangChain message.

    Args:
        message_dict: The message dictionary.

    Returns:
        The LangChain message.
    """
    role = message_dict.get("role", "assistant")
    content = message_dict.get("content", "")
    
    if role == "user":
        return HumanMessage(content=content)
    elif role == "assistant":
        return AIMessage(content=content)
    elif role == "system":
        return SystemMessage(content=content)
    else:
        return ChatMessage(role=role, content=content)


class ChatDeepAI(BaseChatModel):
    """
    DeepAI chat model for LangChain.
    
    This class provides a LangChain interface to DeepAI's chat completion API,
    supporting multiple models and chat styles for various use cases.
    
    Supported Models:
        - standard: General purpose conversational AI (default)
        - math: Mathematics and problem-solving specialized model
        - online: Web-aware model with access to current information
        - code: Programming and development focused model
    
    Supported Chat Styles:
        - chatgpt-alternative: Default conversational style (default)
        - ai-code: Programming and development focused
        - mathematics: Mathematical reasoning focused
        - goku: Enthusiastic and energetic character style
        - gojo_9: Confident and charismatic character style
        - professional: Business and professional communication
        - creative: Creative and imaginative style
        - casual: Relaxed and informal style
    
    Example:
        ```python
        from langchain_deepai import ChatDeepAI
        
        # Initialize with API key
        chat = ChatDeepAI(
            api_key="your-deepai-api-key",
            model="standard",
            chat_style="chatgpt-alternative"
        )
        
        # Use with LangChain
        from langchain_core.messages import HumanMessage
        
        messages = [HumanMessage(content="Hello, how are you?")]
        response = chat.invoke(messages)
        print(response.content)
        ```
    
    Environment Variables:
        Set DEEPAI_API_KEY or DEEPAI_KEY to avoid passing api_key parameter.
    """
    
    model_name: str = Field(default="standard", alias="model")
    """Model name to use. Available: standard, math, online, code."""
    
    chat_style: str = Field(default="chatgpt-alternative")
    """Chat style to use. Affects the personality and response format."""
    
    api_key: Optional[SecretStr] = Field(default=None, alias="deepai_api_key")
    """DeepAI API key. Can also be set via DEEPAI_API_KEY environment variable."""
    
    base_url: str = Field(default="https://api.deepai.org")
    """Base URL for DeepAI API."""
    
    max_tokens: Optional[int] = Field(default=None)
    """Maximum number of tokens to generate."""
    
    temperature: Optional[float] = Field(default=None)
    """Temperature for response generation (if supported)."""
    
    session_id: Optional[str] = Field(default=None)
    """Session ID for maintaining conversation context."""
    
    request_timeout: Optional[float] = Field(default=60.0)
    """Timeout for API requests in seconds."""
    
    max_retries: int = Field(default=3)
    """Maximum number of retries for failed requests."""
    
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Additional keyword arguments to pass to the model."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra kwargs from additional model kwargs."""
        extra = values.get("model_kwargs", {})
        forbidden_keys = {
            "model_name",
            "chat_style", 
            "api_key",
            "base_url",
            "max_tokens",
            "temperature",
            "session_id",
            "request_timeout",
            "max_retries"
        }
        
        for key in list(values.keys()):
            if key not in forbidden_keys:
                if key not in extra:
                    extra[key] = values.pop(key)
        
        values["model_kwargs"] = extra
        return values
    
    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that api key and other required parameters exist."""
        api_key_str = self.api_key.get_secret_value() if self.api_key else None
        validated_key = check_api_key(api_key_str, warn=False)  # Don't warn during init
        
        if validated_key:
            self.api_key = SecretStr(validated_key)
        else:
            # Don't fail if no API key - let user handle it during request
            pass
        
        # Validate model
        if not validate_model(self.model_name):
            available_models = list(get_models().keys())
            logger.warning(
                f"Model '{self.model_name}' not recognized. "
                f"Available models: {available_models}"
            )
        
        # Validate and normalize chat style
        if not validate_chat_style(self.chat_style):
            available_styles = list(get_chat_styles().keys())
            logger.warning(
                f"Chat style '{self.chat_style}' not recognized. "
                f"Available styles: {available_styles}. Using 'chatgpt-alternative' as fallback."
            )
            # Use default style as fallback
            self.chat_style = "chatgpt-alternative"
        else:
            # Normalize the chat style (handle aliases)
            self.chat_style = normalize_chat_style(self.chat_style)
        
        return self
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key after initialization.
        
        Args:
            api_key: The DeepAI API key to set.
        """
        self.api_key = SecretStr(api_key)
    
    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "deepai-chat"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "chat_style": self.chat_style,
            "base_url": self.base_url,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
    
    def _make_api_request(
        self,
        messages: List[Dict[str, Any]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make API request to DeepAI using the deepai package directly."""
        # Get API key from multiple sources
        api_key_str = None
        
        # Try to get API key from instance
        if self.api_key:
            api_key_str = self.api_key.get_secret_value()
        
        # If not found, try environment variables
        if not api_key_str:
            api_key_str = check_api_key()
        
        # If still not found, try to get from kwargs
        if not api_key_str:
            api_key_str = kwargs.get('api_key') or kwargs.get('deepai_api_key')
        
        # If no API key found anywhere, use empty string (make it optional)
        if not api_key_str:
            api_key_str = ""  # Send empty string instead of raising error
        
        # Use the deepai package directly for compatibility
        try:
            from deepai import DeepAI
            
            # Initialize the deepai client
            client = DeepAI()
            # Set API key if available
            if api_key_str and hasattr(client, 'api_key'):
                client.api_key = api_key_str
            
            # Convert our format to deepai package format
            deepai_messages = []
            for msg in messages:
                deepai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Call the deepai package - handle empty API key gracefully
            if api_key_str:
                response = client.chat.completions.create(
                    model=self.model_name,
                    chat_style=self.chat_style,
                    messages=deepai_messages
                )
            else:
                # Try without API key or return mock response
                try:
                    response = client.chat.completions.create(
                        model=self.model_name,
                        chat_style=self.chat_style,
                        messages=deepai_messages
                    )
                except Exception:
                    # Return mock response when no API key
                    return {
                        "output": "I'm a mock response since no API key was provided. Please set your DeepAI API key to get real responses."
                    }
            
            # Convert response format
            if hasattr(response, 'choices') and response.choices:
                return {
                    "output": response.choices[0].message.content
                }
            elif isinstance(response, dict) and 'choices' in response:
                return {
                    "output": response['choices'][0]['message']['content']
                }
            else:
                return {"output": str(response)}
                
        except ImportError:
            # Fallback to direct API if deepai package not available
            if not api_key_str:
                # Return mock response when no deepai package and no API key
                return {
                    "output": "Mock response: DeepAI package not available and no API key provided. Please install deepai package or provide an API key."
                }
            return self._make_direct_api_request(messages, api_key_str, **kwargs)
        except Exception as e:
            logger.warning(f"Error with deepai package: {e}")
            # Fallback to direct API or mock response
            if not api_key_str:
                return {
                    "output": "Mock response due to error and no API key. Please provide a valid DeepAI API key for real responses."
                }
            return self._make_direct_api_request(messages, api_key_str, **kwargs)
    
    def _make_direct_api_request(
        self,
        messages: List[Dict[str, Any]],
        api_key: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Fallback direct API request method."""
        headers = get_auth_headers(api_key)
        
        # Prepare request data to match the working deepai package format
        data = {
            "model": self.model_name,
            "chat_style": self.chat_style,
            "messages": messages,  # Use messages directly, not chatHistory
        }
        
        # Add optional parameters
        if self.max_tokens:
            data["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            data["temperature"] = self.temperature
        if self.session_id:
            data["session_id"] = self.session_id
        
        # Add model kwargs
        data.update(self.model_kwargs)
        data.update(kwargs)
        
        # Make request - Use the correct DeepAI endpoint
        url = f"{self.base_url}/api/v1/chat"
        
        start_time = time.time()
        
        try:
            # Check if API key is empty and return mock response
            if not headers.get("api-key"):
                logger.warning("No API key provided, returning mock response")
                return {"output": f"Mock response for {self.model_name} with chat style {self.chat_style}. This is a placeholder response since no API key was provided."}
            
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            
            response_time = time.time() - start_time
            log_api_call(
                endpoint="chat_completion",
                model=self.model_name,
                chat_style=self.chat_style,
                message_count=len(messages),
                response_time=response_time
            )
            
            # Parse response
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {"output": response.text}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepAI API request failed: {e}")
            # Return mock response on request failure when no API key
            if not headers.get("api-key"):
                logger.warning("Request failed but no API key provided, returning mock response")
                return {"output": f"Mock response for {self.model_name}. API request failed but no API key was provided."}
            raise e
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat completion."""
        # Convert messages to dict format
        message_dicts = [_convert_message_to_dict(m) for m in messages]
        
        # Validate messages
        for msg_dict in message_dicts:
            if not validate_message_format(msg_dict):
                raise ValueError(f"Invalid message format: {msg_dict}")
        
        try:
            # Make API request
            response_data = self._make_api_request(message_dicts, **kwargs)
            
            # Parse response
            content = parse_deepai_response(response_data)
            
            # Create response message
            message = AIMessage(content=content)
            
            # Create generation
            generation = ChatGeneration(
                message=message,
                generation_info={
                    "model": self.model_name,
                    "chat_style": self.chat_style,
                    "finish_reason": "stop"
                }
            )
            
            return ChatResult(generations=[generation])
        
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            raise e
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generate chat completion."""
        # For now, use sync implementation
        # TODO: Implement proper async version
        return self._generate(messages, stop, run_manager, **kwargs)
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available models.
        
        Returns:
            Dictionary containing model information.
        """
        return get_models()
    
    def get_available_chat_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available chat styles.
        
        Returns:
            Dictionary containing chat style information.
        """
        return get_chat_styles()
    
    def set_session_id(self, session_id: str) -> None:
        """
        Set session ID for conversation context.
        
        Args:
            session_id: Session identifier for maintaining context.
        """
        self.session_id = session_id
    
    def clear_session(self) -> None:
        """Clear the current session ID."""
        self.session_id = None
