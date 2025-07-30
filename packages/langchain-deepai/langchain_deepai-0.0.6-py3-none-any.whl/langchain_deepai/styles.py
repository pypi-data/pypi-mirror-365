"""
Chat style management utilities for langchain-deepai package.

This module provides utilities for fetching and managing chat styles
from the DeepAI API, integrating with the deepai package's ChatStyleManager.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def get_all_styles() -> List[Dict[str, Any]]:
    """
    Fetch all available chat styles from DeepAI using the ChatStyleManager.
    
    This function integrates with the deepai package's ChatStyleManager to retrieve
    a comprehensive list of all available chat styles with their metadata including
    id, url_handle (which becomes the chat_style), name, description, genre, usage, and image.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing chat style information.
        Each dictionary contains:
        - id: Unique identifier for the style
        - url_handle: The chat style identifier used in ChatDeepAI
        - name: Display name of the chat style
        - description: Detailed description of the style's personality
        - genre: Category/genre of the style (e.g., 'History', 'Anime', etc.)
        - usage: Usage count/popularity
        - image: Image URL for the style
        
    Example:
        >>> from langchain_deepai.styles import get_all_styles
        >>> styles = get_all_styles()
        >>> for style in styles[:2]:  # Show first 2 styles
        ...     print(f"Style: {style['name']} ({style['url_handle']})")
        ...     print(f"Description: {style['description']}")
        Style: Albert Einstein (albert-einstein)
        Description: I am Albert Einstein, renowned physicist...
        Style: Goku (goku)
        Description: I'm Goku, a Saiyan warrior from Dragon Ball series...
        
    Raises:
        ImportError: If the deepai package is not installed
        Exception: If there's an error fetching styles from the API
    """
    try:
        from deepai import ChatStyleManager
        
        # Create ChatStyleManager instance
        style_manager = ChatStyleManager()
        
        # Fetch all chat styles
        chat_styles = style_manager.get_chat_styles()
        
        logger.info(f"Successfully fetched {len(chat_styles)} chat styles from DeepAI")
        return chat_styles
        
    except ImportError as e:
        logger.warning("deepai package not installed, returning local fallback styles")
        # Return fallback styles if deepai package is not available
        return _get_fallback_styles()
        
    except Exception as e:
        logger.error(f"Error fetching chat styles from DeepAI: {e}")
        # Return fallback styles on any error
        return _get_fallback_styles()


def get_style_by_handle(url_handle: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific chat style by its url_handle (chat_style identifier).
    
    Args:
        url_handle (str): The url_handle/chat_style identifier to search for
        
    Returns:
        Optional[Dict[str, Any]]: The chat style dictionary if found, None otherwise
        
    Example:
        >>> from langchain_deepai.styles import get_style_by_handle
        >>> goku_style = get_style_by_handle('goku')
        >>> if goku_style:
        ...     print(f"Found: {goku_style['name']}")
        Found: Goku
    """
    styles = get_all_styles()
    for style in styles:
        if style.get('url_handle') == url_handle:
            return style
    return None


def get_styles_by_genre(genre: str) -> List[Dict[str, Any]]:
    """
    Get all chat styles belonging to a specific genre.
    
    Args:
        genre (str): The genre to filter by (e.g., 'History', 'Anime', etc.)
        
    Returns:
        List[Dict[str, Any]]: List of chat styles in the specified genre
        
    Example:
        >>> from langchain_deepai.styles import get_styles_by_genre
        >>> anime_styles = get_styles_by_genre('Anime')
        >>> print(f"Found {len(anime_styles)} anime styles")
    """
    styles = get_all_styles()
    return [style for style in styles if style.get('genre', '').lower() == genre.lower()]


def get_available_genres() -> List[str]:
    """
    Get a list of all available genres from the chat styles.
    
    Returns:
        List[str]: List of unique genres
        
    Example:
        >>> from langchain_deepai.styles import get_available_genres
        >>> genres = get_available_genres()
        >>> print("Available genres:", genres)
    """
    styles = get_all_styles()
    genres = set()
    for style in styles:
        if 'genre' in style and style['genre']:
            genres.add(style['genre'])
    return sorted(list(genres))


def search_styles(query: str) -> List[Dict[str, Any]]:
    """
    Search for chat styles by name or description.
    
    Args:
        query (str): Search term to look for in name or description
        
    Returns:
        List[Dict[str, Any]]: List of matching chat styles
        
    Example:
        >>> from langchain_deepai.styles import search_styles
        >>> scientist_styles = search_styles('scientist')
        >>> for style in scientist_styles:
        ...     print(style['name'])
    """
    styles = get_all_styles()
    query_lower = query.lower()
    
    matches = []
    for style in styles:
        name = style.get('name', '').lower()
        description = style.get('description', '').lower()
        
        if query_lower in name or query_lower in description:
            matches.append(style)
    
    return matches


def get_popular_styles(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the most popular chat styles sorted by usage.
    
    Args:
        limit (int): Maximum number of styles to return
        
    Returns:
        List[Dict[str, Any]]: List of popular chat styles sorted by usage
        
    Example:
        >>> from langchain_deepai.styles import get_popular_styles
        >>> popular = get_popular_styles(5)
        >>> for style in popular:
        ...     print(f"{style['name']}: {style['usage']} uses")
    """
    styles = get_all_styles()
    # Sort by usage count (descending)
    sorted_styles = sorted(styles, key=lambda x: x.get('usage', 0), reverse=True)
    return sorted_styles[:limit]


def _get_fallback_styles() -> List[Dict[str, Any]]:
    """
    Fallback chat styles when DeepAI API is not available.
    
    Returns:
        List[Dict[str, Any]]: List of fallback chat styles
    """
    return [
        {
            'id': 1,
            'url_handle': 'chatgpt-alternative',
            'name': 'ChatGPT Alternative',
            'description': 'Default conversational style similar to ChatGPT. Helpful, harmless, and honest.',
            'genre': 'General',
            'usage': 10000,
            'image': 'chat-style-image/default/chatgpt-alternative.jpg'
        },
        {
            'id': 2,
            'url_handle': 'ai-code',
            'name': 'AI Code Assistant',
            'description': 'Programming and development focused conversational style. Technical, precise, and solution-oriented.',
            'genre': 'Programming',
            'usage': 8500,
            'image': 'chat-style-image/default/ai-code.jpg'
        },
        {
            'id': 3,
            'url_handle': 'mathematics',
            'name': 'Mathematics Expert',
            'description': 'Mathematical reasoning and problem-solving style. Analytical, step-by-step, and methodical.',
            'genre': 'Education',
            'usage': 7200,
            'image': 'chat-style-image/default/mathematics.jpg'
        },
        {
            'id': 30,
            'url_handle': 'albert-einstein',
            'name': 'Albert Einstein',
            'description': 'I am Albert Einstein, renowned physicist known for developing the theory of relativity. Ask me about my views on science, philosophy, or my personal life.',
            'genre': 'History',
            'usage': 1000,
            'image': 'chat-style-image/default/albert-einstein.jpg'
        },
        {
            'id': 3015,
            'url_handle': 'goku',
            'name': 'Goku',
            'description': "I'm Goku, a Saiyan warrior from Dragon Ball series. With intense training & battles, I've achieved Super Saiyan forms. Ask me about my adventures, my Kamehameha technique, or my friends like Vegeta and Krillin.",
            'genre': 'Anime',
            'usage': 2500,
            'image': 'chat-style-image/default/goku.jpg'
        },
        {
            'id': 4,
            'url_handle': 'professional',
            'name': 'Professional Assistant',
            'description': 'Business and professional communication style. Formal, reliable, and business-focused.',
            'genre': 'Business',
            'usage': 6800,
            'image': 'chat-style-image/default/professional.jpg'
        },
        {
            'id': 5,
            'url_handle': 'creative',
            'name': 'Creative Writer',
            'description': 'Creative and imaginative conversational style. Creative, imaginative, and expressive.',
            'genre': 'Creative',
            'usage': 5400,
            'image': 'chat-style-image/default/creative.jpg'
        },
        {
            'id': 6,
            'url_handle': 'casual',
            'name': 'Casual Chat',
            'description': 'Relaxed and informal conversational style. Casual, friendly, and approachable.',
            'genre': 'General',
            'usage': 4900,
            'image': 'chat-style-image/default/casual.jpg'
        }
    ]


def list_all_handles() -> List[str]:
    """
    Get a simple list of all available chat style handles (url_handle values).
    
    Returns:
        List[str]: List of all url_handle values that can be used as chat_style
        
    Example:
        >>> from langchain_deepai.styles import list_all_handles
        >>> handles = list_all_handles()
        >>> print("Available chat styles:", handles)
    """
    styles = get_all_styles()
    return [style.get('url_handle') for style in styles if style.get('url_handle')]


def validate_style_handle(handle: str) -> bool:
    """
    Validate if a chat style handle exists.
    
    Args:
        handle (str): The chat style handle to validate
        
    Returns:
        bool: True if the handle exists, False otherwise
        
    Example:
        >>> from langchain_deepai.styles import validate_style_handle
        >>> print(validate_style_handle('goku'))  # True
        >>> print(validate_style_handle('invalid'))  # False
    """
    available_handles = list_all_handles()
    return handle in available_handles


# Example usage and testing
if __name__ == "__main__":
    print("🎨 LangChain-DeepAI Chat Styles Manager")
    print("=" * 45)
    
    # Get all styles
    print("\n1. Fetching All Chat Styles:")
    styles = get_all_styles()
    print(f"   Found {len(styles)} chat styles")
    
    # Show first few styles
    print("\n2. Sample Chat Styles:")
    for i, style in enumerate(styles[:3]):
        print(f"   {i+1}. {style['name']} ({style['url_handle']})")
        print(f"      Genre: {style['genre']}")
        print(f"      Usage: {style['usage']}")
        print(f"      Description: {style['description'][:60]}...")
        print()
    
    # Show available genres
    print("3. Available Genres:")
    genres = get_available_genres()
    print(f"   {', '.join(genres)}")
    
    # Show popular styles
    print("\n4. Most Popular Styles:")
    popular = get_popular_styles(5)
    for i, style in enumerate(popular):
        print(f"   {i+1}. {style['name']}: {style['usage']} uses")
    
    # Show all handles
    print("\n5. All Available Chat Style Handles:")
    handles = list_all_handles()
    print(f"   {', '.join(handles)}")
    
    print(f"\n✅ Chat styles management complete!")
    print(f"\n📋 Usage:")
    print(f"   from langchain_deepai.styles import get_all_styles")
    print(f"   styles = get_all_styles()")
    print(f"   # Use style['url_handle'] as chat_style in ChatDeepAI")
