"""Speech capabilities for langchain-deepai (TTS and STT)."""

from .text_to_speech import TextToSpeechDeepAI
from .speech_to_text import SpeechToTextDeepAI

__all__ = [
    'TextToSpeechDeepAI',
    'SpeechToTextDeepAI',
]
