"""Authentication utilities for DeepAI integration."""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def check_api_key(api_key: Optional[str] = None, warn: bool = False) -> Optional[str]:
    """
    Check and validate DeepAI API key.
    
    Args:
        api_key: Optional API key. If not provided, will check environment variables.
        warn: Whether to log warning if no key is found.
        
    Returns:
        Valid API key if found, None otherwise.
    """
    if api_key:
        return api_key
    
    # Check environment variables
    env_key = os.getenv("DEEPAI_API_KEY") or os.getenv("DEEPAI_KEY")
    
    if env_key:
        return env_key
    
    if warn:
        logger.warning(
            "No DeepAI API key found. Please provide an API key either:\n"
            "1. As a parameter: ChatDeepAI(api_key='your-key')\n"
            "2. Set environment variable: DEEPAI_API_KEY=your-key\n"
            "3. Set environment variable: DEEPAI_KEY=your-key"
        )
    
    return None


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate the format of a DeepAI API key.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if the format appears valid, False otherwise.
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation - DeepAI keys are typically alphanumeric
    if len(api_key) < 10:  # Minimum reasonable length
        return False
    
    return True


def get_auth_headers(api_key: Optional[str] = None) -> dict:
    """
    Get authentication headers for DeepAI API requests.
    
    Args:
        api_key: Optional API key
        
    Returns:
        Dictionary containing authentication headers.
    """
    validated_key = check_api_key(api_key)
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "langchain-deepai/1.0.0"
    }
    
    if validated_key:
        headers["Api-Key"] = validated_key
    
    return headers
