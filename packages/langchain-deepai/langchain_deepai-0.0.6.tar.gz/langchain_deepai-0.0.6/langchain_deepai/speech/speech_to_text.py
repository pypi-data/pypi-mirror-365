"""DeepAI Speech-to-Text for LangChain."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Union, BinaryIO
import io
import os

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


class SpeechToTextDeepAI:
    """
    DeepAI Speech-to-Text client for LangChain integration.
    
    This class provides speech-to-text capabilities using DeepAI's STT API,
    allowing conversion of audio files to text transcriptions.
    
    Supported Features:
        - High-accuracy speech recognition
        - Multiple audio format support
        - Language detection and transcription
        - Batch processing capabilities
    
    Supported Audio Formats:
        - WAV: Uncompressed audio format
        - MP3: Compressed audio format  
        - M4A: Apple audio format
        - FLAC: Lossless compression
        - OGG: Open-source audio format
    
    Example:
        ```python
        from langchain_deepai import SpeechToTextDeepAI
        
        # Initialize STT client
        stt = SpeechToTextDeepAI(api_key="your-deepai-api-key")
        
        # Transcribe audio file
        result = stt.transcribe("audio_file.wav")
        print(result["text"])
        
        # Transcribe with additional options
        result = stt.transcribe(
            "audio_file.wav",
            language="en",
            return_timestamps=True
        )
        ```
    
    Environment Variables:
        Set DEEPAI_API_KEY or DEEPAI_KEY to avoid passing api_key parameter.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepai.org/api",
        request_timeout: float = 120.0,
        max_retries: int = 3
    ):
        """
        Initialize SpeechToTextDeepAI client.
        
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
    
    def get_supported_formats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get supported audio formats and their descriptions.
        
        Returns:
            Dictionary containing format information.
        """
        return {
            "wav": {
                "description": "Waveform Audio File Format",
                "mime_type": "audio/wav",
                "compression": "uncompressed",
                "quality": "highest",
                "recommended_for": "Best quality transcription"
            },
            "mp3": {
                "description": "MPEG Audio Layer III",
                "mime_type": "audio/mpeg",
                "compression": "lossy",
                "quality": "good",
                "recommended_for": "General use, smaller file sizes"
            },
            "m4a": {
                "description": "MPEG-4 Audio",
                "mime_type": "audio/mp4",
                "compression": "lossy",
                "quality": "good",
                "recommended_for": "Apple ecosystem, voice recordings"
            },
            "flac": {
                "description": "Free Lossless Audio Codec",
                "mime_type": "audio/flac",
                "compression": "lossless",
                "quality": "high",
                "recommended_for": "High-quality audio with compression"
            },
            "ogg": {
                "description": "Ogg Vorbis",
                "mime_type": "audio/ogg",
                "compression": "lossy",
                "quality": "good",
                "recommended_for": "Open-source applications"
            }
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get supported languages for transcription.
        
        Returns:
            Dictionary mapping language codes to language names.
        """
        return {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "hi": "Hindi",
            "auto": "Auto-detect"
        }
    
    def _make_stt_request(
        self,
        audio_file: Union[str, BinaryIO, bytes],
        language: str = "auto",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make STT request to DeepAI API."""
        headers = get_auth_headers(self.api_key)
        
        # Remove Content-Type to let requests set it with boundary for multipart
        if "Content-Type" in headers:
            del headers["Content-Type"]
        
        # Prepare files for upload
        files = {}
        data = {
            "language": language
        }
        data.update(kwargs)
        
        if isinstance(audio_file, str):
            # File path
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            with open(audio_file, "rb") as f:
                files["audio"] = f
                
                # STT endpoint
                url = f"{self.base_url}/speech-to-text"
                
                start_time = time.time()
                
                try:
                    response = requests.post(
                        url,
                        data=data,
                        files=files,
                        headers=headers,
                        timeout=self.request_timeout
                    )
                    response.raise_for_status()
                    
                    response_time = time.time() - start_time
                    log_api_call(
                        endpoint="speech_to_text",
                        model="stt",
                        chat_style=language,
                        message_count=1,
                        response_time=response_time
                    )
                    
                    return response.json()
                
                except requests.exceptions.RequestException as e:
                    logger.error(f"DeepAI STT request failed: {e}")
                    raise e
        
        elif isinstance(audio_file, bytes):
            # Raw bytes
            files["audio"] = io.BytesIO(audio_file)
            
            url = f"{self.base_url}/speech-to-text"
            
            start_time = time.time()
            
            try:
                response = requests.post(
                    url,
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=self.request_timeout
                )
                response.raise_for_status()
                
                response_time = time.time() - start_time
                log_api_call(
                    endpoint="speech_to_text",
                    model="stt",
                    chat_style=language,
                    message_count=1,
                    response_time=response_time
                )
                
                return response.json()
            
            except requests.exceptions.RequestException as e:
                logger.error(f"DeepAI STT request failed: {e}")
                raise e
        
        elif hasattr(audio_file, 'read'):
            # File-like object
            files["audio"] = audio_file
            
            url = f"{self.base_url}/speech-to-text"
            
            start_time = time.time()
            
            try:
                response = requests.post(
                    url,
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=self.request_timeout
                )
                response.raise_for_status()
                
                response_time = time.time() - start_time
                log_api_call(
                    endpoint="speech_to_text",
                    model="stt",
                    chat_style=language,
                    message_count=1,
                    response_time=response_time
                )
                
                return response.json()
            
            except requests.exceptions.RequestException as e:
                logger.error(f"DeepAI STT request failed: {e}")
                raise e
        
        else:
            raise ValueError("audio_file must be a file path, bytes, or file-like object")
    
    def transcribe(
        self,
        audio_file: Union[str, BinaryIO, bytes],
        language: str = "auto",
        return_timestamps: bool = False,
        return_confidence: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio_file: Audio file path, bytes, or file-like object
            language: Language code for transcription ("auto" for auto-detect)
            return_timestamps: Whether to return word timestamps
            return_confidence: Whether to return confidence scores
            **kwargs: Additional STT parameters
            
        Returns:
            Dictionary containing:
                - text: Transcribed text
                - language: Detected/used language
                - metadata: Transcription metadata
                - timestamps: Word timestamps (if requested)
                - confidence: Confidence scores (if requested)
        """
        # Add optional parameters
        if return_timestamps:
            kwargs["return_timestamps"] = True
        if return_confidence:
            kwargs["return_confidence"] = True
        
        # Make API request
        response_data = self._make_stt_request(audio_file, language, **kwargs)
        
        # Extract transcription
        text = response_data.get("text", response_data.get("output", ""))
        if not text:
            raise ValueError("No transcription text in response")
        
        # Prepare result
        result = {
            "text": text,
            "language": language,
            "metadata": {
                "timestamp": get_current_timestamp(),
                "request_id": create_request_id(),
                "language_requested": language,
                "return_timestamps": return_timestamps,
                "return_confidence": return_confidence,
                **kwargs
            }
        }
        
        # Add optional data if available
        if "timestamps" in response_data:
            result["timestamps"] = response_data["timestamps"]
        
        if "confidence" in response_data:
            result["confidence"] = response_data["confidence"]
        
        if "detected_language" in response_data:
            result["metadata"]["detected_language"] = response_data["detected_language"]
        
        return result
    
    def transcribe_multiple(
        self,
        audio_files: List[Union[str, BinaryIO, bytes]],
        language: str = "auto",
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files.
        
        Args:
            audio_files: List of audio files to transcribe
            language: Language code for transcription
            **kwargs: Additional STT parameters
            
        Returns:
            List of dictionaries containing transcription results.
        """
        results = []
        
        for i, audio_file in enumerate(audio_files):
            file_id = audio_file if isinstance(audio_file, str) else f"file_{i+1}"
            logger.info(f"Transcribing audio {i+1}/{len(audio_files)}: {file_id}")
            
            try:
                result = self.transcribe(audio_file, language, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to transcribe audio {i+1}: {e}")
                results.append({
                    "error": str(e),
                    "file": file_id,
                    "metadata": {"failed": True}
                })
        
        return results
    
    def get_file_info(self, audio_file: str) -> Dict[str, Any]:
        """
        Get information about an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with file information.
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        file_size = os.path.getsize(audio_file)
        file_ext = os.path.splitext(audio_file)[1].lower().lstrip('.')
        
        formats = self.get_supported_formats()
        
        return {
            "filepath": audio_file,
            "filename": os.path.basename(audio_file),
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "file_extension": file_ext,
            "is_supported_format": file_ext in formats,
            "format_info": formats.get(file_ext, {"description": "Unknown format"}),
            "estimated_processing_time": file_size / 1000000 * 5  # Rough estimate: 5 seconds per MB
        }
