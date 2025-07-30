"""langchain-deepai: Comprehensive DeepAI integration for LangChain with all capabilities."""

# Core functionality
from langchain_deepai.core import get_models, get_chat_styles, DeepAIProvider

# Text generation and chat
from langchain_deepai.text import (
    ChatDeepAI,
    DeepAIMath,
    DeepAICode,
    DeepAIOnline,
    DeepAIProfessional,
    DeepAICreative,
    DeepAICasual
)

# Image capabilities
from langchain_deepai.images import ImageDeepAI, generate_image

# Speech capabilities - TTS and STT
from langchain_deepai.speech import TextToSpeechDeepAI, SpeechToTextDeepAI

# API key generation utilities
from langchain_deepai.keys import (
    generate_test_key,
    generate_multiple_test_keys,
    quick_test_key,
    mock_deepai_key,
    is_test_key,
    validate_test_key_format
)

# Chat styles management
from langchain_deepai.styles import (
    get_all_styles,
    get_style_by_handle,
    get_styles_by_genre,
    get_available_genres,
    search_styles,
    get_popular_styles,
    list_all_handles,
    validate_style_handle
)

# Chat styles management
from langchain_deepai.styles import (
    get_all_styles,
    get_style_by_handle,
    get_styles_by_genre,
    get_available_genres,
    search_styles,
    get_popular_styles,
    list_all_handles,
    validate_style_handle
)

__all__ = [
    # Core
    "get_models",
    "get_chat_styles", 
    "DeepAIProvider",
    # Text/Chat
    "ChatDeepAI",
    "DeepAIMath",
    "DeepAICode",
    "DeepAIOnline",
    "DeepAIProfessional",
    "DeepAICreative",
    "DeepAICasual",
    # Images
    "ImageDeepAI",
    "generate_image",
    # Speech
    "TextToSpeechDeepAI",
    "SpeechToTextDeepAI",
    # API Keys
    "generate_test_key",
    "generate_multiple_test_keys",
    "quick_test_key",
    "mock_deepai_key",
    "is_test_key",
    "validate_test_key_format",
    # Chat Styles
    "get_all_styles",
    "get_style_by_handle", 
    "get_styles_by_genre",
    "get_available_genres",
    "search_styles",
    "get_popular_styles",
    "list_all_handles",
    "validate_style_handle",
    # Chat Styles
    "get_all_styles",
    "get_style_by_handle",
    "get_styles_by_genre", 
    "get_available_genres",
    "search_styles",
    "get_popular_styles",
    "list_all_handles",
    "validate_style_handle",
]

__version__ = "1.0.0"
__author__ = "DeepAI LangChain Integration"
__description__ = "LangChain integration for DeepAI API with chat, images, and speech capabilities"
