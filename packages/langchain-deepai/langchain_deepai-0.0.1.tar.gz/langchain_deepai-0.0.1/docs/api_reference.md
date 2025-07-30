# LangChain DeepAI API Reference

## Overview

The `langchain-deepai` package provides comprehensive integration between LangChain and DeepAI's API services. This package follows the same architectural patterns as `langchain-openai` and `langchain-g4f` for consistency and familiarity.

## Package Structure

```
langchain-deepai/
├── core/                     # Core utilities and providers
│   ├── providers.py         # Model and style management
│   ├── authentication.py   # API key handling
│   └── utils.py            # Utility functions
├── text/                    # Chat and text generation
│   ├── base.py             # Main ChatDeepAI class
│   └── specialized.py      # Specialized chat models
├── images/                  # Image generation
│   └── image_generation.py # Image generation classes
├── speech/                  # Speech capabilities
│   ├── text_to_speech.py   # TTS functionality
│   └── speech_to_text.py   # STT functionality
└── examples/               # Usage examples
```

## Core Module

### Providers (`langchain_deepai.core.providers`)

#### Functions

**`get_models() -> Dict[str, Dict[str, Any]]`**

Returns information about available DeepAI models.

```python
from langchain_deepai.core import get_models

models = get_models()
# Returns:
# {
#     "standard": {
#         "description": "General purpose conversational AI model",
#         "capabilities": ["chat", "text_generation", "general_qa"],
#         "best_for": "General conversations and text generation"
#     },
#     "math": {...},
#     "online": {...},
#     "code": {...}
# }
```

**`get_chat_styles() -> Dict[str, Dict[str, Any]]`**

Returns information about available chat styles.

```python
from langchain_deepai.core import get_chat_styles

styles = get_chat_styles()
# Returns detailed information about each chat style
```

**`validate_model(model: str) -> bool`**

Validates if a model name is supported.

**`validate_chat_style(chat_style: str) -> bool`**

Validates if a chat style is supported.

### Authentication (`langchain_deepai.core.authentication`)

**`check_api_key(api_key: Optional[str] = None) -> Optional[str]`**

Checks and validates DeepAI API key from parameter or environment variables.

**`get_auth_headers(api_key: Optional[str] = None) -> dict`**

Returns authentication headers for API requests.

## Text Module

### ChatDeepAI (`langchain_deepai.text.ChatDeepAI`)

The main chat model class that inherits from LangChain's `BaseChatModel`.

#### Parameters

- **`model_name`** (str): Model to use ("standard", "math", "online", "code"). Default: "standard"
- **`chat_style`** (str): Chat style to use. Default: "chatgpt-alternative"
- **`api_key`** (Optional[SecretStr]): DeepAI API key
- **`base_url`** (str): Base URL for DeepAI API
- **`max_tokens`** (Optional[int]): Maximum tokens to generate
- **`temperature`** (Optional[float]): Response randomness
- **`session_id`** (Optional[str]): Session ID for context
- **`request_timeout`** (float): Request timeout in seconds
- **`max_retries`** (int): Maximum retry attempts

#### Methods

**`invoke(messages: List[BaseMessage], **kwargs) -> AIMessage`**

Generate a response to the given messages.

```python
from langchain_deepai import ChatDeepAI
from langchain_core.messages import HumanMessage

chat = ChatDeepAI(api_key="your-key")
response = chat.invoke([HumanMessage(content="Hello!")])
```

**`set_session_id(session_id: str) -> None`**

Set session ID for conversation context.

**`clear_session() -> None`**

Clear the current session ID.

**`get_available_models() -> Dict[str, Dict[str, Any]]`**

Get information about available models.

**`get_available_chat_styles() -> Dict[str, Dict[str, Any]]`**

Get information about available chat styles.

### Specialized Models

All specialized models inherit from `ChatDeepAI` with optimized defaults.

#### DeepAIMath

Mathematics-focused model using "math" model and "mathematics" style.

```python
from langchain_deepai import DeepAIMath

math_chat = DeepAIMath(api_key="your-key")
response = math_chat.invoke([HumanMessage(content="Solve: 2x + 5 = 15")])
```

#### DeepAICode

Programming-focused model using "code" model and "ai-code" style.

```python
from langchain_deepai import DeepAICode

code_chat = DeepAICode(api_key="your-key")
response = code_chat.invoke([HumanMessage(content="Write a Python sorting function")])
```

#### DeepAIOnline

Web-aware model using "online" model for current information.

#### DeepAIProfessional

Business communication model using "professional" style.

#### DeepAICreative

Creative writing model using "creative" style.

#### DeepAICasual

Casual conversation model using "casual" style.

## Images Module

### ImageDeepAI (`langchain_deepai.images.ImageDeepAI`)

Image generation client for creating images from text prompts.

#### Parameters

- **`api_key`** (Optional[str]): DeepAI API key
- **`base_url`** (str): Base URL for DeepAI API
- **`request_timeout`** (float): Request timeout in seconds
- **`max_retries`** (int): Maximum retry attempts

#### Methods

**`generate(prompt: str, model: str = "text2img", **kwargs) -> Dict[str, Any]`**

Generate an image from text prompt.

```python
from langchain_deepai import ImageDeepAI

image_gen = ImageDeepAI(api_key="your-key")
result = image_gen.generate(
    prompt="A beautiful sunset over mountains",
    model="text2img",
    width=512,
    height=512
)

# Save image
with open("sunset.jpg", "wb") as f:
    f.write(result["image_data"])
```

**`generate_and_save(prompt: str, filepath: str, **kwargs) -> Dict[str, Any]`**

Generate and save image to file.

**`generate_multiple(prompts: List[str], **kwargs) -> List[Dict[str, Any]]`**

Generate multiple images from a list of prompts.

**`get_available_models() -> Dict[str, Dict[str, Any]]`**

Get available image generation models.

### Available Image Models

- **text2img**: Standard text-to-image generation
- **fantasy-world-generator**: Fantasy themed images
- **cyberpunk-generator**: Cyberpunk aesthetic
- **old-style-generator**: Vintage and classic styles
- **renaissance-painting-generator**: Renaissance art style
- **abstract-painting-generator**: Abstract art
- **impressionism-painting-generator**: Impressionist style
- **surreal-graphics-generator**: Surreal and dreamlike images

### Convenience Function

**`generate_image(prompt: str, **kwargs) -> Dict[str, Any]`**

Convenience function for generating a single image.

```python
from langchain_deepai import generate_image

result = generate_image(
    prompt="A serene mountain landscape",
    model="text2img",
    api_key="your-key"
)
```

## Speech Module

### TextToSpeechDeepAI (`langchain_deepai.speech.TextToSpeechDeepAI`)

Text-to-speech synthesis client.

#### Methods

**`synthesize(text: str, voice: str = "default", **kwargs) -> Dict[str, Any]`**

Convert text to speech.

```python
from langchain_deepai import TextToSpeechDeepAI

tts = TextToSpeechDeepAI(api_key="your-key")
result = tts.synthesize(
    text="Hello, this is a test.",
    voice="default"
)

# Save audio
with open("speech.wav", "wb") as f:
    f.write(result["audio_data"])
```

**`synthesize_and_save(text: str, filepath: str, **kwargs) -> Dict[str, Any]`**

Convert text to speech and save to file.

**`synthesize_multiple(texts: List[str], **kwargs) -> List[Dict[str, Any]]`**

Convert multiple texts to speech.

**`get_available_voices() -> Dict[str, Dict[str, Any]]`**

Get available TTS voices.

**`get_text_length_estimate(text: str) -> Dict[str, Any]`**

Estimate synthesis duration and cost.

### SpeechToTextDeepAI (`langchain_deepai.speech.SpeechToTextDeepAI`)

Speech-to-text transcription client.

#### Methods

**`transcribe(audio_file: Union[str, BinaryIO, bytes], **kwargs) -> Dict[str, Any]`**

Transcribe audio to text.

```python
from langchain_deepai import SpeechToTextDeepAI

stt = SpeechToTextDeepAI(api_key="your-key")
result = stt.transcribe("audio_file.wav", language="auto")
print(result["text"])
```

**`transcribe_multiple(audio_files: List[...], **kwargs) -> List[Dict[str, Any]]`**

Transcribe multiple audio files.

**`get_supported_formats() -> Dict[str, Dict[str, Any]]`**

Get supported audio formats.

**`get_supported_languages() -> Dict[str, str]`**

Get supported languages for transcription.

**`get_file_info(audio_file: str) -> Dict[str, Any]`**

Get information about an audio file.

## Environment Variables

Set these environment variables to avoid passing API keys in code:

- **`DEEPAI_API_KEY`**: Your DeepAI API key
- **`DEEPAI_KEY`**: Alternative environment variable name

## Error Handling

All classes include proper error handling and logging:

```python
import logging

# Enable logging to see API calls and errors
logging.basicConfig(level=logging.INFO)

try:
    chat = ChatDeepAI(api_key="your-key")
    response = chat.invoke([HumanMessage(content="Hello")])
except Exception as e:
    print(f"Error: {e}")
```

## LangChain Integration Examples

### With Chains

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_deepai import ChatDeepAI

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a short story about {topic}"
)

chain = LLMChain(
    llm=ChatDeepAI(chat_style="creative"),
    prompt=prompt
)

result = chain.run(topic="time travel")
```

### With Agents

```python
from langchain.agents import initialize_agent, Tool
from langchain_deepai import ChatDeepAI, ImageDeepAI

def generate_image_tool(prompt: str) -> str:
    image_gen = ImageDeepAI()
    result = image_gen.generate(prompt)
    return f"Image generated: {result['image_url']}"

tools = [
    Tool(
        name="ImageGenerator",
        func=generate_image_tool,
        description="Generate images from text descriptions"
    )
]

agent = initialize_agent(
    tools=tools,
    llm=ChatDeepAI(),
    agent="zero-shot-react-description"
)
```

## Best Practices

1. **API Key Management**: Use environment variables for API keys
2. **Error Handling**: Always wrap API calls in try-catch blocks
3. **Logging**: Enable logging for debugging and monitoring
4. **Session Management**: Use session IDs for multi-turn conversations
5. **Model Selection**: Choose appropriate models for specific tasks
6. **Rate Limiting**: Be mindful of API rate limits and usage costs

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `langchain-core` is installed
2. **API Key Errors**: Verify your DeepAI API key is correct
3. **Model Not Found**: Use `get_models()` to check available models
4. **Network Issues**: Check your internet connection and API status
