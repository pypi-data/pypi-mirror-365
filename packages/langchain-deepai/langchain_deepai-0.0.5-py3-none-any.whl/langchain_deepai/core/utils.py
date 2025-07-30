"""Utility functions for DeepAI LangChain integration."""

import json
import time
import uuid
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


def create_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def get_current_timestamp() -> int:
    """Get current Unix timestamp."""
    return int(time.time())


def format_messages_for_deepai(messages: List[Dict[str, Any]]) -> str:
    """
    Format LangChain messages for DeepAI API.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        JSON string formatted for DeepAI API.
    """
    try:
        return json.dumps(messages)
    except (TypeError, ValueError) as e:
        logger.error(f"Error formatting messages for DeepAI: {e}")
        return json.dumps([])


def parse_deepai_response(response_data: Union[Dict, str]) -> str:
    """
    Parse response from DeepAI API.
    
    Args:
        response_data: Raw response from DeepAI API
        
    Returns:
        Parsed content string.
    """
    if isinstance(response_data, str):
        return response_data
    
    if isinstance(response_data, dict):
        # Try different possible response keys
        content = (
            response_data.get("output") or
            response_data.get("text") or
            response_data.get("content") or
            response_data.get("response") or
            str(response_data)
        )
        return content
    
    return str(response_data)


def validate_message_format(message: Dict[str, Any]) -> bool:
    """
    Validate that a message has the correct format.
    
    Args:
        message: Message dictionary to validate
        
    Returns:
        True if valid, False otherwise.
    """
    required_keys = {"role", "content"}
    return (
        isinstance(message, dict) and
        required_keys.issubset(message.keys()) and
        message["role"] in {"user", "assistant", "system"}
    )


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize input text for API requests.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return text


def merge_kwargs_with_defaults(kwargs: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge user kwargs with default parameters.
    
    Args:
        kwargs: User-provided keyword arguments
        defaults: Default parameters
        
    Returns:
        Merged parameters dictionary.
    """
    merged = defaults.copy()
    merged.update(kwargs)
    return merged


def extract_error_message(response: Union[Dict, str, Exception]) -> str:
    """
    Extract error message from various response types.
    
    Args:
        response: Response that may contain error information
        
    Returns:
        Error message string.
    """
    if isinstance(response, Exception):
        return str(response)
    
    if isinstance(response, dict):
        return (
            response.get("error") or
            response.get("message") or
            response.get("detail") or
            "Unknown error occurred"
        )
    
    return str(response)


def log_api_call(
    endpoint: str,
    model: str,
    chat_style: str,
    message_count: int,
    response_time: Optional[float] = None
) -> None:
    """
    Log API call information for debugging.
    
    Args:
        endpoint: API endpoint called
        model: Model used
        chat_style: Chat style used
        message_count: Number of messages in request
        response_time: Response time in seconds
    """
    log_msg = f"DeepAI API call - Endpoint: {endpoint}, Model: {model}, Style: {chat_style}, Messages: {message_count}"
    
    if response_time:
        log_msg += f", Response time: {response_time:.2f}s"
    
    logger.info(log_msg)
