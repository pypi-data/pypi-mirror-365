"""DeepAI image generation for LangChain."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Union, BinaryIO
import io
import base64

try:
    import requests
    from PIL import Image
except ImportError as e:
    raise ImportError(
        "Could not import required packages. "
        "Please install them with `pip install requests pillow`."
    ) from e

from ..core.authentication import check_api_key, get_auth_headers
from ..core.utils import create_request_id, get_current_timestamp, log_api_call

logger = logging.getLogger(__name__)


class ImageDeepAI:
    """
    DeepAI image generation client for LangChain integration.
    
    This class provides image generation capabilities using DeepAI's API,
    compatible with LangChain workflows and patterns.
    
    Supported Features:
        - Text-to-image generation
        - Various artistic styles and models
        - High-quality image output
        - Customizable image parameters
    
    Available Models/Styles:
        - text2img: Standard text-to-image generation
        - fantasy-world-generator: Fantasy and magical themes
        - cyberpunk-generator: Cyberpunk and futuristic themes
        - old-style-generator: Vintage and classic art styles
        - renaissance-painting-generator: Renaissance art style
        - abstract-painting-generator: Abstract art generation
        - impressionism-painting-generator: Impressionist style
        - surreal-graphics-generator: Surreal and dreamlike images
    
    Example:
        ```python
        from langchain_deepai import ImageDeepAI
        
        # Initialize image generator
        image_gen = ImageDeepAI(api_key="your-deepai-api-key")
        
        # Generate image
        result = image_gen.generate(
            prompt="A beautiful sunset over mountains",
            style="text2img",
            width=512,
            height=512
        )
        
        # Save image
        with open("sunset.jpg", "wb") as f:
            f.write(result["image_data"])
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
        Initialize ImageDeepAI client.
        
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
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available image generation models and their descriptions.
        
        Returns:
            Dictionary containing model information.
        """
        return {
            "text2img": {
                "description": "Standard text-to-image generation",
                "best_for": "General image generation from text descriptions",
                "style": "Realistic and diverse",
                "endpoint": "text2img"
            },
            "fantasy-world-generator": {
                "description": "Fantasy and magical themed image generation",
                "best_for": "Fantasy art, magical scenes, mythical creatures",
                "style": "Fantasy and magical",
                "endpoint": "fantasy-world-generator"
            },
            "cyberpunk-generator": {
                "description": "Cyberpunk and futuristic themed generation",
                "best_for": "Sci-fi scenes, cyberpunk aesthetics, futuristic concepts",
                "style": "Cyberpunk and futuristic",
                "endpoint": "cyberpunk-generator"
            },
            "old-style-generator": {
                "description": "Vintage and classic art style generation",
                "best_for": "Vintage aesthetics, classical art styles",
                "style": "Vintage and classical",
                "endpoint": "old-style-generator"
            },
            "renaissance-painting-generator": {
                "description": "Renaissance art style generation",
                "best_for": "Classical paintings, renaissance aesthetics",
                "style": "Renaissance art",
                "endpoint": "renaissance-painting-generator"
            },
            "abstract-painting-generator": {
                "description": "Abstract art generation",
                "best_for": "Abstract art, artistic expressions",
                "style": "Abstract and artistic",
                "endpoint": "abstract-painting-generator"
            },
            "impressionism-painting-generator": {
                "description": "Impressionist style generation",
                "best_for": "Impressionist paintings, soft artistic style",
                "style": "Impressionist",
                "endpoint": "impressionism-painting-generator"
            },
            "surreal-graphics-generator": {
                "description": "Surreal and dreamlike image generation",
                "best_for": "Surreal art, dreamlike scenes, abstract concepts",
                "style": "Surreal and dreamlike",
                "endpoint": "surreal-graphics-generator"
            }
        }
    
    def _make_image_request(
        self,
        prompt: str,
        model: str = "text2img",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make image generation request to DeepAI API."""
        headers = get_auth_headers(self.api_key)
        
        # Get model info
        models = self.get_available_models()
        if model not in models:
            raise ValueError(f"Model '{model}' not supported. Available: {list(models.keys())}")
        
        endpoint = models[model]["endpoint"]
        url = f"{self.base_url}/{endpoint}"
        
        # Prepare request data
        data = {"text": prompt}
        data.update(kwargs)
        
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
                endpoint=f"image_generation/{endpoint}",
                model=model,
                chat_style="N/A",
                message_count=1,
                response_time=response_time
            )
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepAI image generation request failed: {e}")
            raise e
    
    def generate(
        self,
        prompt: str,
        model: str = "text2img",
        width: Optional[int] = None,
        height: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate an image from text prompt.
        
        Args:
            prompt: Text description of the image to generate
            model: Image generation model to use
            width: Image width (if supported by model)
            height: Image height (if supported by model)
            **kwargs: Additional parameters for image generation
            
        Returns:
            Dictionary containing:
                - image_url: URL of the generated image
                - image_data: Raw image data (bytes)
                - metadata: Generation metadata
        """
        # Add dimensions if provided
        if width:
            kwargs["width"] = width
        if height:
            kwargs["height"] = height
        
        # Make API request
        response_data = self._make_image_request(prompt, model, **kwargs)
        
        # Extract image URL
        image_url = response_data.get("output_url")
        if not image_url:
            raise ValueError("No image URL in response")
        
        # Download image data
        try:
            img_response = requests.get(image_url, timeout=self.request_timeout)
            img_response.raise_for_status()
            image_data = img_response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download generated image: {e}")
            raise e
        
        return {
            "image_url": image_url,
            "image_data": image_data,
            "metadata": {
                "prompt": prompt,
                "model": model,
                "timestamp": get_current_timestamp(),
                "request_id": create_request_id(),
                "width": width,
                "height": height,
                **kwargs
            }
        }
    
    def generate_and_save(
        self,
        prompt: str,
        filepath: str,
        model: str = "text2img",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate an image and save it to file.
        
        Args:
            prompt: Text description of the image to generate
            filepath: Path where to save the generated image
            model: Image generation model to use
            **kwargs: Additional parameters for image generation
            
        Returns:
            Dictionary containing generation metadata and file path.
        """
        result = self.generate(prompt, model, **kwargs)
        
        # Save image to file
        with open(filepath, "wb") as f:
            f.write(result["image_data"])
        
        result["metadata"]["filepath"] = filepath
        
        logger.info(f"Image saved to: {filepath}")
        
        return result
    
    def generate_multiple(
        self,
        prompts: List[str],
        model: str = "text2img",
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images from a list of prompts.
        
        Args:
            prompts: List of text descriptions
            model: Image generation model to use
            **kwargs: Additional parameters for image generation
            
        Returns:
            List of dictionaries containing generation results.
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            logger.info(f"Generating image {i+1}/{len(prompts)}: {prompt[:50]}...")
            
            try:
                result = self.generate(prompt, model, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to generate image {i+1}: {e}")
                results.append({
                    "error": str(e),
                    "prompt": prompt,
                    "metadata": {"failed": True}
                })
        
        return results


def generate_image(
    prompt: str,
    api_key: Optional[str] = None,
    model: str = "text2img",
    width: Optional[int] = None,
    height: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Convenience function for generating a single image.
    
    Args:
        prompt: Text description of the image to generate
        api_key: DeepAI API key (optional if set in environment)
        model: Image generation model to use
        width: Image width
        height: Image height
        **kwargs: Additional parameters
        
    Returns:
        Dictionary containing image data and metadata.
    
    Example:
        ```python
        from langchain_deepai import generate_image
        
        result = generate_image(
            prompt="A serene mountain landscape at sunset",
            model="text2img",
            width=512,
            height=512
        )
        
        # Save the image
        with open("landscape.jpg", "wb") as f:
            f.write(result["image_data"])
        ```
    """
    client = ImageDeepAI(api_key=api_key)
    return client.generate(prompt, model, width, height, **kwargs)
