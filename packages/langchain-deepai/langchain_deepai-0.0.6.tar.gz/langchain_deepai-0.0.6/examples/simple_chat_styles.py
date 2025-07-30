#!/usr/bin/env python3
"""
Simple script to quickly list all available chat styles in langchain-deepai.
"""

from langchain_deepai import get_chat_styles


def get_all_chat_styles():
    """
    Get a simple list of all available chat styles.
    
    Returns:
        list: List of all available chat style names
    """
    chat_styles = get_chat_styles()
    return list(chat_styles.keys())


def get_chat_styles_with_descriptions():
    """
    Get chat styles with their descriptions.
    
    Returns:
        dict: Dictionary with style names as keys and descriptions as values
    """
    chat_styles = get_chat_styles()
    return {style: info['description'] for style, info in chat_styles.items()}


def print_chat_styles():
    """Print all available chat styles in a simple format."""
    styles = get_all_chat_styles()
    
    print("Available Chat Styles:")
    print("=" * 25)
    for i, style in enumerate(styles, 1):
        print(f"{i:2}. {style}")
    
    print(f"\nTotal: {len(styles)} chat styles available")


def print_chat_styles_detailed():
    """Print chat styles with descriptions."""
    styles = get_chat_styles_with_descriptions()
    
    print("Available Chat Styles with Descriptions:")
    print("=" * 45)
    for style, description in styles.items():
        print(f"• {style}")
        print(f"  {description}")
        print()


if __name__ == "__main__":
    # Simple list
    print_chat_styles()
    print("\n" + "="*50 + "\n")
    
    # Detailed list
    print_chat_styles_detailed()
    
    # For use in code
    print("For use in your code:")
    print("```python")
    print("from langchain_deepai import get_chat_styles")
    print("styles = list(get_chat_styles().keys())")
    print("print(styles)")
    print("```")
