"""Specialized DeepAI chat models for specific use cases."""

from typing import Any, Dict, List, Optional
from .base import ChatDeepAI


class DeepAIMath(ChatDeepAI):
    """
    Mathematics-focused DeepAI chat model for LangChain.
    
    This specialized model is optimized for mathematical reasoning, problem-solving,
    and mathematical computations. It uses the 'math' model with 'mathematics' chat style.
    
    Best for:
        - Solving mathematical equations
        - Mathematical proofs and derivations
        - Statistical analysis and calculations
        - Physics and engineering problems
        - Step-by-step mathematical explanations
    
    Example:
        ```python
        from langchain_deepai import DeepAIMath
        from langchain_core.messages import HumanMessage
        
        math_chat = DeepAIMath(api_key="your-api-key")
        
        messages = [HumanMessage(content="Solve the equation: 2x + 5 = 15")]
        response = math_chat.invoke(messages)
        print(response.content)
        ```
    
    The model will provide detailed mathematical explanations and show work steps.
    """
    
    def __init__(self, **kwargs):
        # Set math-specific defaults
        kwargs.setdefault("model_name", "math")
        kwargs.setdefault("chat_style", "mathematics")
        super().__init__(**kwargs)


class DeepAICode(ChatDeepAI):
    """
    Programming-focused DeepAI chat model for LangChain.
    
    This specialized model is optimized for programming tasks, code generation,
    debugging, and software development discussions. It uses the 'code' model
    with 'ai-code' chat style.
    
    Best for:
        - Code generation and completion
        - Debugging and error analysis
        - Code review and optimization
        - Algorithm design and implementation
        - Programming language explanations
        - Software architecture discussions
    
    Example:
        ```python
        from langchain_deepai import DeepAICode
        from langchain_core.messages import HumanMessage
        
        code_chat = DeepAICode(api_key="your-api-key")
        
        messages = [HumanMessage(content="Write a Python function to calculate factorial")]
        response = code_chat.invoke(messages)
        print(response.content)
        ```
    
    The model will provide technical, precise responses with code examples and explanations.
    """
    
    def __init__(self, **kwargs):
        # Set code-specific defaults
        kwargs.setdefault("model_name", "code")
        kwargs.setdefault("chat_style", "ai-code")
        super().__init__(**kwargs)


class DeepAIOnline(ChatDeepAI):
    """
    Web-aware DeepAI chat model for LangChain.
    
    This specialized model has access to current information and can provide
    up-to-date responses about recent events, current data, and real-time information.
    It uses the 'online' model with 'chatgpt-alternative' chat style.
    
    Best for:
        - Current events and news
        - Real-time data queries
        - Stock market information
        - Weather updates
        - Recent developments in various fields
        - Questions requiring up-to-date information
    
    Example:
        ```python
        from langchain_deepai import DeepAIOnline
        from langchain_core.messages import HumanMessage
        
        online_chat = DeepAIOnline(api_key="your-api-key")
        
        messages = [HumanMessage(content="What are the latest developments in AI?")]
        response = online_chat.invoke(messages)
        print(response.content)
        ```
    
    The model will search for and provide current information in its responses.
    """
    
    def __init__(self, **kwargs):
        # Set online-specific defaults
        kwargs.setdefault("model_name", "online")
        kwargs.setdefault("chat_style", "chatgpt-alternative")
        super().__init__(**kwargs)


class DeepAIProfessional(ChatDeepAI):
    """
    Business and professional communication DeepAI chat model for LangChain.
    
    This specialized model is optimized for formal business communications,
    professional writing, and corporate interactions. It uses the 'standard'
    model with 'professional' chat style.
    
    Best for:
        - Business correspondence
        - Professional reports and documents
        - Formal presentations
        - Corporate communications
        - Policy and procedure documentation
        - Executive summaries
    
    Example:
        ```python
        from langchain_deepai import DeepAIProfessional
        from langchain_core.messages import HumanMessage
        
        prof_chat = DeepAIProfessional(api_key="your-api-key")
        
        messages = [HumanMessage(content="Draft a professional email about project delays")]
        response = prof_chat.invoke(messages)
        print(response.content)
        ```
    
    The model will provide formal, authoritative responses suitable for business contexts.
    """
    
    def __init__(self, **kwargs):
        # Set professional-specific defaults
        kwargs.setdefault("model_name", "standard")
        kwargs.setdefault("chat_style", "professional")
        super().__init__(**kwargs)


class DeepAICreative(ChatDeepAI):
    """
    Creative and imaginative DeepAI chat model for LangChain.
    
    This specialized model is optimized for creative writing, artistic discussions,
    and imaginative content generation. It uses the 'standard' model with
    'creative' chat style.
    
    Best for:
        - Creative writing and storytelling
        - Poetry and artistic expression
        - Brainstorming creative ideas
        - Character and world building
        - Marketing copy and creative content
        - Artistic project planning
    
    Example:
        ```python
        from langchain_deepai import DeepAICreative
        from langchain_core.messages import HumanMessage
        
        creative_chat = DeepAICreative(api_key="your-api-key")
        
        messages = [HumanMessage(content="Write a short story about a time traveler")]
        response = creative_chat.invoke(messages)
        print(response.content)
        ```
    
    The model will provide imaginative, expressive responses with creative flair.
    """
    
    def __init__(self, **kwargs):
        # Set creative-specific defaults
        kwargs.setdefault("model_name", "standard")
        kwargs.setdefault("chat_style", "creative")
        super().__init__(**kwargs)


class DeepAICasual(ChatDeepAI):
    """
    Casual and informal DeepAI chat model for LangChain.
    
    This specialized model is optimized for relaxed, informal conversations
    and casual interactions. It uses the 'standard' model with 'casual' chat style.
    
    Best for:
        - Casual conversations
        - Informal advice and suggestions
        - Friendly interactions
        - Personal assistance
        - Relaxed Q&A sessions
        - Entertainment and fun interactions
    
    Example:
        ```python
        from langchain_deepai import DeepAICasual
        from langchain_core.messages import HumanMessage
        
        casual_chat = DeepAICasual(api_key="your-api-key")
        
        messages = [HumanMessage(content="What's a good movie to watch tonight?")]
        response = casual_chat.invoke(messages)
        print(response.content)
        ```
    
    The model will provide friendly, approachable responses in a casual tone.
    """
    
    def __init__(self, **kwargs):
        # Set casual-specific defaults
        kwargs.setdefault("model_name", "standard")
        kwargs.setdefault("chat_style", "casual")
        super().__init__(**kwargs)
