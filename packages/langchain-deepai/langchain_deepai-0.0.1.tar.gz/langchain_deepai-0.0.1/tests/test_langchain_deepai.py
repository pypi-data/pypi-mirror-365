"""Tests for langchain-deepai package."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
from langchain_deepai import ChatDeepAI, DeepAIMath, DeepAICode
from langchain_deepai import ImageDeepAI, generate_image
from langchain_deepai import TextToSpeechDeepAI, SpeechToTextDeepAI
from langchain_deepai.core.providers import get_models, get_chat_styles
from langchain_deepai.core.authentication import check_api_key
from langchain_core.messages import HumanMessage, AIMessage


class TestChatDeepAI:
    """Test ChatDeepAI functionality."""
    
    def test_initialization(self):
        """Test ChatDeepAI initialization."""
        chat = ChatDeepAI(api_key="test-key")
        assert chat.model_name == "standard"
        assert chat.chat_style == "chatgpt-alternative"
        assert chat.api_key.get_secret_value() == "test-key"
    
    def test_custom_parameters(self):
        """Test initialization with custom parameters."""
        chat = ChatDeepAI(
            api_key="test-key",
            model_name="math",
            chat_style="mathematics",
            max_tokens=100,
            temperature=0.7
        )
        assert chat.model_name == "math"
        assert chat.chat_style == "mathematics"
        assert chat.max_tokens == 100
        assert chat.temperature == 0.7
    
    @patch('langchain_deepai.text.base.requests.post')
    def test_generate(self, mock_post):
        """Test chat generation."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {"output": "Hello! How can I help you?"}
        mock_post.return_value = mock_response
        
        chat = ChatDeepAI(api_key="test-key")
        messages = [HumanMessage(content="Hello")]
        
        result = chat._generate(messages)
        
        assert len(result.generations) == 1
        assert isinstance(result.generations[0].message, AIMessage)
        assert result.generations[0].message.content == "Hello! How can I help you?"
    
    def test_session_management(self):
        """Test session ID management."""
        chat = ChatDeepAI(api_key="test-key")
        
        assert chat.session_id is None
        
        chat.set_session_id("test-session")
        assert chat.session_id == "test-session"
        
        chat.clear_session()
        assert chat.session_id is None


class TestSpecializedModels:
    """Test specialized chat models."""
    
    def test_deepai_math_initialization(self):
        """Test DeepAIMath initialization."""
        math_chat = DeepAIMath(api_key="test-key")
        assert math_chat.model_name == "math"
        assert math_chat.chat_style == "mathematics"
    
    def test_deepai_code_initialization(self):
        """Test DeepAICode initialization."""
        code_chat = DeepAICode(api_key="test-key")
        assert code_chat.model_name == "code"
        assert code_chat.chat_style == "ai-code"


class TestImageDeepAI:
    """Test ImageDeepAI functionality."""
    
    def test_initialization(self):
        """Test ImageDeepAI initialization."""
        image_gen = ImageDeepAI(api_key="test-key")
        assert image_gen.api_key == "test-key"
        assert image_gen.base_url == "https://api.deepai.org/api"
    
    def test_get_available_models(self):
        """Test getting available models."""
        image_gen = ImageDeepAI(api_key="test-key")
        models = image_gen.get_available_models()
        
        assert isinstance(models, dict)
        assert "text2img" in models
        assert "fantasy-world-generator" in models
        assert "cyberpunk-generator" in models
    
    @patch('langchain_deepai.images.image_generation.requests.post')
    @patch('langchain_deepai.images.image_generation.requests.get')
    def test_generate_image(self, mock_get, mock_post):
        """Test image generation."""
        # Mock API response
        mock_post_response = Mock()
        mock_post_response.raise_for_status.return_value = None
        mock_post_response.json.return_value = {"output_url": "https://example.com/image.jpg"}
        mock_post.return_value = mock_post_response
        
        # Mock image download
        mock_get_response = Mock()
        mock_get_response.raise_for_status.return_value = None
        mock_get_response.content = b"fake_image_data"
        mock_get.return_value = mock_get_response
        
        image_gen = ImageDeepAI(api_key="test-key")
        result = image_gen.generate("A beautiful sunset", model="text2img")
        
        assert result["image_url"] == "https://example.com/image.jpg"
        assert result["image_data"] == b"fake_image_data"
        assert "metadata" in result


class TestTextToSpeechDeepAI:
    """Test TextToSpeechDeepAI functionality."""
    
    def test_initialization(self):
        """Test TTS initialization."""
        tts = TextToSpeechDeepAI(api_key="test-key")
        assert tts.api_key == "test-key"
        assert tts.base_url == "https://api.deepai.org/api"
    
    def test_get_available_voices(self):
        """Test getting available voices."""
        tts = TextToSpeechDeepAI(api_key="test-key")
        voices = tts.get_available_voices()
        
        assert isinstance(voices, dict)
        assert "default" in voices
        assert "female" in voices
        assert "male" in voices
    
    def test_get_text_length_estimate(self):
        """Test text length estimation."""
        tts = TextToSpeechDeepAI(api_key="test-key")
        
        text = "Hello world"
        estimate = tts.get_text_length_estimate(text)
        
        assert "word_count" in estimate
        assert "character_count" in estimate
        assert "estimated_duration_seconds" in estimate
        assert estimate["word_count"] == 2
        assert estimate["character_count"] == len(text)


class TestSpeechToTextDeepAI:
    """Test SpeechToTextDeepAI functionality."""
    
    def test_initialization(self):
        """Test STT initialization."""
        stt = SpeechToTextDeepAI(api_key="test-key")
        assert stt.api_key == "test-key"
        assert stt.base_url == "https://api.deepai.org/api"
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        stt = SpeechToTextDeepAI(api_key="test-key")
        formats = stt.get_supported_formats()
        
        assert isinstance(formats, dict)
        assert "wav" in formats
        assert "mp3" in formats
        assert "m4a" in formats
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        stt = SpeechToTextDeepAI(api_key="test-key")
        languages = stt.get_supported_languages()
        
        assert isinstance(languages, dict)
        assert "en" in languages
        assert "auto" in languages


class TestCoreProviders:
    """Test core provider functionality."""
    
    def test_get_models(self):
        """Test getting available models."""
        models = get_models()
        
        assert isinstance(models, dict)
        assert "standard" in models
        assert "math" in models
        assert "online" in models
        assert "code" in models
        
        # Check model structure
        for model_name, model_info in models.items():
            assert "description" in model_info
            assert "capabilities" in model_info
            assert "best_for" in model_info
    
    def test_get_chat_styles(self):
        """Test getting available chat styles."""
        styles = get_chat_styles()
        
        assert isinstance(styles, dict)
        assert "chatgpt-alternative" in styles
        assert "ai-code" in styles
        assert "mathematics" in styles
        
        # Check style structure
        for style_name, style_info in styles.items():
            assert "description" in style_info
            assert "personality" in style_info
            assert "best_for" in style_info


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_check_api_key_with_key(self):
        """Test API key validation with provided key."""
        key = check_api_key("test-api-key")
        assert key == "test-api-key"
    
    @patch.dict(os.environ, {"DEEPAI_API_KEY": "env-api-key"})
    def test_check_api_key_from_env(self):
        """Test API key from environment variable."""
        key = check_api_key()
        assert key == "env-api-key"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_check_api_key_none(self):
        """Test API key when none provided."""
        key = check_api_key()
        assert key is None


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('langchain_deepai.images.image_generation.ImageDeepAI.generate')
    def test_generate_image_function(self, mock_generate):
        """Test generate_image convenience function."""
        mock_generate.return_value = {
            "image_url": "https://example.com/test.jpg",
            "image_data": b"test_data",
            "metadata": {}
        }
        
        result = generate_image("test prompt", api_key="test-key")
        
        mock_generate.assert_called_once()
        assert result["image_url"] == "https://example.com/test.jpg"


if __name__ == "__main__":
    pytest.main([__file__])
