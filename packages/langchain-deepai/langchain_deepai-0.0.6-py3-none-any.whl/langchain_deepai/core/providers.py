"""DeepAI providers and model management."""

from enum import Enum
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DeepAIProvider(Enum):
    """Available DeepAI providers and endpoints."""
    
    STANDARD = "standard"
    MATH = "math"
    ONLINE = "online"
    CODE = "code"
    IMAGE_GENERATION = "image_generation"
    TEXT_TO_SPEECH = "text_to_speech"
    SPEECH_TO_TEXT = "speech_to_text"


def get_models() -> Dict[str, Dict[str, Any]]:
    """
    Get available DeepAI models with their capabilities.
    
    Returns:
        Dict containing model information with capabilities, descriptions, and usage examples.
    """
    return {
        "standard": {
            "description": "General purpose conversational AI model",
            "capabilities": ["chat", "text_generation", "general_qa"],
            "best_for": "General conversations and text generation",
            "example_use_cases": [
                "Customer support",
                "General Q&A", 
                "Content creation",
                "Casual conversation"
            ]
        },
        "math": {
            "description": "Mathematics and problem-solving specialized model",
            "capabilities": ["mathematical_reasoning", "problem_solving", "calculations"],
            "best_for": "Mathematical computations and reasoning",
            "example_use_cases": [
                "Solving equations",
                "Mathematical proofs",
                "Statistical analysis",
                "Physics problems"
            ]
        },
        "online": {
            "description": "Web-aware model with access to current information",
            "capabilities": ["web_search", "current_events", "real_time_data"],
            "best_for": "Questions requiring current information",
            "example_use_cases": [
                "Current events",
                "Stock prices",
                "Weather information",
                "Recent news"
            ]
        },
        "code": {
            "description": "Programming and development focused model",
            "capabilities": ["code_generation", "debugging", "code_review"],
            "best_for": "Software development and coding tasks",
            "example_use_cases": [
                "Code generation",
                "Bug fixing",
                "Code explanation",
                "Algorithm design"
            ]
        }
    }


def get_chat_styles() -> Dict[str, Dict[str, Any]]:
    """
    Get available DeepAI chat styles with descriptions.
    
    Returns:
        Dict containing chat style information with descriptions and recommended use cases.
    """
    return {
        "chatgpt-alternative": {
            "description": "Default conversational style similar to ChatGPT",
            "personality": "Helpful, harmless, and honest",
            "best_for": "General conversations",
            "tone": "Professional yet friendly"
        },
        "ai-code": {
            "description": "Programming and development focused conversational style",
            "personality": "Technical, precise, and solution-oriented",
            "best_for": "Coding assistance and technical discussions",
            "tone": "Technical and direct"
        },
        "mathematics": {
            "description": "Mathematical reasoning and problem-solving style",
            "personality": "Analytical, step-by-step, and methodical",
            "best_for": "Mathematical problems and scientific discussions",
            "tone": "Academic and systematic"
        },
        "goku": {
            "description": "Enthusiastic and energetic character-based style",
            "personality": "Energetic, optimistic, and determined",
            "best_for": "Motivational conversations and entertainment",
            "tone": "Enthusiastic and inspiring"
        },
        "gojo_9": {
            "description": "Confident and charismatic character-based style",
            "personality": "Confident, charismatic, and slightly playful",
            "best_for": "Engaging conversations with personality",
            "tone": "Confident and charismatic"
        },
        "professional": {
            "description": "Business and professional communication style",
            "personality": "Formal, reliable, and business-focused",
            "best_for": "Business communications and formal discussions",
            "tone": "Professional and authoritative"
        },
        "creative": {
            "description": "Creative and imaginative conversational style",
            "personality": "Creative, imaginative, and expressive",
            "best_for": "Creative writing and artistic discussions",
            "tone": "Creative and expressive"
        },
        "casual": {
            "description": "Relaxed and informal conversational style",
            "personality": "Casual, friendly, and approachable",
            "best_for": "Informal conversations and casual interactions",
            "tone": "Casual and friendly"
        }
    }


def get_model_for_task(task: str) -> str:
    """
    Get the recommended model for a specific task.
    
    Args:
        task: The type of task ("chat", "math", "code", "online", etc.)
        
    Returns:
        Recommended model name for the task.
    """
    task_model_mapping = {
        "chat": "standard",
        "conversation": "standard", 
        "general": "standard",
        "math": "math",
        "mathematics": "math",
        "calculation": "math",
        "code": "code",
        "programming": "code",
        "development": "code",
        "online": "online",
        "current": "online",
        "web": "online",
        "search": "online"
    }
    
    return task_model_mapping.get(task.lower(), "standard")


def get_style_for_task(task: str) -> str:
    """
    Get the recommended chat style for a specific task.
    
    Args:
        task: The type of task or conversation style needed
        
    Returns:
        Recommended chat style for the task.
    """
    task_style_mapping = {
        "chat": "chatgpt-alternative",
        "conversation": "chatgpt-alternative",
        "general": "chatgpt-alternative",
        "math": "mathematics",
        "mathematics": "mathematics",
        "calculation": "mathematics",
        "code": "ai-code",
        "programming": "ai-code",
        "development": "ai-code",
        "business": "professional",
        "formal": "professional",
        "creative": "creative",
        "art": "creative",
        "casual": "casual",
        "informal": "casual",
        "entertainment": "goku",
        "motivational": "goku"
    }
    
    return task_style_mapping.get(task.lower(), "chatgpt-alternative")


def validate_model(model: str) -> bool:
    """
    Validate if a model name is supported.
    
    Args:
        model: Model name to validate
        
    Returns:
        True if model is supported, False otherwise.
    """
    supported_models = get_models().keys()
    return model in supported_models


def validate_chat_style(chat_style: str, strict: bool = False) -> bool:
    """
    Validate if a chat style is supported.
    
    Args:
        chat_style: Chat style to validate
        strict: If True, only accept predefined styles. If False, accept any style.
        
    Returns:
        True if chat style is supported or if strict=False, False otherwise.
    """
    if not strict:
        # In non-strict mode, accept any non-empty string as a valid chat style
        return bool(chat_style and isinstance(chat_style, str) and chat_style.strip())
    
    # In strict mode, check against supported styles and aliases
    supported_styles = get_chat_styles().keys()
    # Also accept common aliases
    aliases = {
        "chat": "chatgpt-alternative",
        "default": "chatgpt-alternative", 
        "general": "chatgpt-alternative",
        "standard": "chatgpt-alternative"
    }
    
    # Try to get from external styles module if available
    try:
        from ..styles import validate_style_handle
        if validate_style_handle(chat_style):
            return True
    except ImportError:
        pass
    
    return chat_style in supported_styles or chat_style in aliases


def normalize_chat_style(chat_style: str) -> str:
    """
    Normalize chat style name to a supported style.
    
    Args:
        chat_style: Chat style to normalize
        
    Returns:
        Normalized chat style name.
    """
    aliases = {
        "chat": "chatgpt-alternative",
        "default": "chatgpt-alternative", 
        "general": "chatgpt-alternative",
        "standard": "chatgpt-alternative"
    }
    
    return aliases.get(chat_style, chat_style)
