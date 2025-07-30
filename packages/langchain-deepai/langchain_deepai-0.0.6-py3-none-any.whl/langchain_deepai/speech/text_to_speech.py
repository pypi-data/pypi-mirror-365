"""DeepAI Text-to-Speech for LangChain."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Union, BinaryIO
import io

try:
    import requests
except ImportError as e:
    raise ImportError(
        "Could not import required packages. "
        "Please install them with `pip install requests`."
    ) from e

from ..core.authentication import check_api_key, get_auth_headers
from ..core.utils import create_request_id, get_current_timestamp, log_api_call

logger = logging.getLogger(__name__)


class TextToSpeechDeepAI:
    """
    DeepAI Text-to-Speech client for LangChain integration.
    
    This class provides text-to-speech capabilities using DeepAI's TTS API,
    allowing conversion of text to natural-sounding speech audio.
    
    Supported Features:
        - High-quality speech synthesis
        - Multiple voice options
        - Customizable speech parameters
        - Audio format options
    
    Available Voices:
        - Default: Standard English voice
        - Additional voices may be available (check API documentation)
    
    Example:
        ```python
        from langchain_deepai import TextToSpeechDeepAI
        
        # Initialize TTS client
        tts = TextToSpeechDeepAI(api_key="your-deepai-api-key")
        
        # Convert text to speech
        result = tts.synthesize(
            text="Hello, this is a test of text-to-speech synthesis.",
            voice="default"
        )
        
        # Save audio file
        with open("speech.wav", "wb") as f:
            f.write(result["audio_data"])
        ```
    
    Environment Variables:
        Set DEEPAI_API_KEY or DEEPAI_KEY to avoid passing api_key parameter.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepai.org/api",
        request_timeout: float = 60.0,
        max_retries: int = 3
    ):
        """
        Initialize TextToSpeechDeepAI client.
        
        Args:
            api_key: DeepAI API key
            base_url: Base URL for DeepAI API
            request_timeout: Timeout for requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = check_api_key(api_key)
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.max_retries = max_retries
    
    def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available TTS voices and their descriptions.
        
        Returns:
            Dictionary containing voice information.
        """
        return {
            "default": {
                "description": "Standard English voice",
                "language": "en-US",
                "gender": "neutral",
                "quality": "high",
                "best_for": "General text-to-speech conversion"
            },
            "female": {
                "description": "Female English voice",
                "language": "en-US", 
                "gender": "female",
                "quality": "high",
                "best_for": "Natural-sounding female narration"
            },
            "male": {
                "description": "Male English voice",
                "language": "en-US",
                "gender": "male", 
                "quality": "high",
                "best_for": "Natural-sounding male narration"
            }
        }
    
    def _make_tts_request(
        self,
        text: str,
        voice: str = "default",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make TTS request to DeepAI API."""
        headers = get_auth_headers(self.api_key)
        
        # Prepare request data
        data = {
            "text": text,
            "voice": voice
        }
        data.update(kwargs)
        
        # TTS endpoint
        url = f"{self.base_url}/text-to-speech"
        
        start_time = time.time()
        
        try:
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            
            response_time = time.time() - start_time
            log_api_call(
                endpoint="text_to_speech",
                model="tts",
                chat_style=voice,
                message_count=1,
                response_time=response_time
            )
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepAI TTS request failed: {e}")
            raise e
    
    def synthesize(
        self,
        text: str,
        voice: str = "default",
        speed: Optional[float] = None,
        pitch: Optional[float] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use for synthesis
            speed: Speech speed (if supported)
            pitch: Speech pitch (if supported)
            **kwargs: Additional TTS parameters
            
        Returns:
            Dictionary containing:
                - audio_url: URL of the generated audio
                - audio_data: Raw audio data (bytes)
                - metadata: Synthesis metadata
        """
        # Validate text length
        if len(text) > 10000:  # Reasonable limit
            logger.warning("Text too long, truncating to 10000 characters")
            text = text[:10000]
        
        # Add optional parameters
        if speed is not None:
            kwargs["speed"] = speed
        if pitch is not None:
            kwargs["pitch"] = pitch
        
        # Make API request
        response_data = self._make_tts_request(text, voice, **kwargs)
        
        # Extract audio URL
        audio_url = response_data.get("output_url")
        if not audio_url:
            raise ValueError("No audio URL in response")
        
        # Download audio data
        try:
            audio_response = requests.get(audio_url, timeout=self.request_timeout)
            audio_response.raise_for_status()
            audio_data = audio_response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download generated audio: {e}")
            raise e
        
        return {
            "audio_url": audio_url,
            "audio_data": audio_data,
            "metadata": {
                "text": text,
                "voice": voice,
                "speed": speed,
                "pitch": pitch,
                "timestamp": get_current_timestamp(),
                "request_id": create_request_id(),
                "text_length": len(text),
                **kwargs
            }
        }
    
    def synthesize_and_save(
        self,
        text: str,
        filepath: str,
        voice: str = "default",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Convert text to speech and save audio to file.
        
        Args:
            text: Text to convert to speech
            filepath: Path where to save the audio file
            voice: Voice to use for synthesis
            **kwargs: Additional TTS parameters
            
        Returns:
            Dictionary containing synthesis metadata and file path.
        """
        result = self.synthesize(text, voice, **kwargs)
        
        # Save audio to file
        with open(filepath, "wb") as f:
            f.write(result["audio_data"])
        
        result["metadata"]["filepath"] = filepath
        
        logger.info(f"Audio saved to: {filepath}")
        
        return result
    
    def synthesize_multiple(
        self,
        texts: List[str],
        voice: str = "default",
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Convert multiple texts to speech.
        
        Args:
            texts: List of texts to convert
            voice: Voice to use for synthesis
            **kwargs: Additional TTS parameters
            
        Returns:
            List of dictionaries containing synthesis results.
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Synthesizing audio {i+1}/{len(texts)}: {text[:50]}...")
            
            try:
                result = self.synthesize(text, voice, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to synthesize audio {i+1}: {e}")
                results.append({
                    "error": str(e),
                    "text": text,
                    "metadata": {"failed": True}
                })
        
        return results
    
    def get_text_length_estimate(self, text: str) -> Dict[str, Any]:
        """
        Estimate the duration and cost of synthesizing given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with estimates.
        """
        word_count = len(text.split())
        char_count = len(text)
        
        # Rough estimates (actual values may vary)
        estimated_duration = word_count * 0.6  # ~0.6 seconds per word
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "estimated_duration_seconds": estimated_duration,
            "estimated_duration_minutes": estimated_duration / 60,
            "is_within_limits": char_count <= 10000
        }
