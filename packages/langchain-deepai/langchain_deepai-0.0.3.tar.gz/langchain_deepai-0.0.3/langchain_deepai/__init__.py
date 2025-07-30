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
]

__version__ = "1.0.0"
__author__ = "DeepAI LangChain Integration"
__description__ = "LangChain integration for DeepAI API with chat, images, and speech capabilities"
