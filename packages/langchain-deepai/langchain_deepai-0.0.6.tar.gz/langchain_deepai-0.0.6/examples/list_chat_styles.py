#!/usr/bin/env python3
"""
List all available chat styles in langchain-deepai package.

This example shows how to discover and use all available chat styles.
"""

from langchain_deepai import ChatDeepAI, get_chat_styles
from langchain_core.messages import HumanMessage


def list_all_chat_styles():
    """List all available chat styles with descriptions."""
    print("🎨 Available Chat Styles in LangChain-DeepAI")
    print("=" * 60)
    
    # Get all chat styles
    chat_styles = get_chat_styles()
    
    print(f"\n📋 Total Available Chat Styles: {len(chat_styles)}")
    print("-" * 60)
    
    for style_name, style_info in chat_styles.items():
        print(f"\n🎯 Style: '{style_name}'")
        print(f"   📝 Description: {style_info['description']}")
        print(f"   👤 Personality: {style_info['personality']}")
        print(f"   ✅ Best For: {style_info['best_for']}")
        print(f"   🎭 Tone: {style_info['tone']}")
    
    return chat_styles


def list_chat_style_aliases():
    """List chat style aliases that map to main styles."""
    print("\n🔗 Chat Style Aliases")
    print("=" * 30)
    
    aliases = {
        "chat": "chatgpt-alternative",
        "default": "chatgpt-alternative", 
        "general": "chatgpt-alternative",
        "standard": "chatgpt-alternative"
    }
    
    print("\n📌 Aliases (these map to main styles):")
    for alias, main_style in aliases.items():
        print(f"   '{alias}' → '{main_style}'")
    
    return aliases


def demonstrate_chat_styles():
    """Demonstrate different chat styles with example responses."""
    print("\n🚀 Chat Style Demonstrations")
    print("=" * 40)
    
    # Get available styles
    chat_styles = get_chat_styles()
    
    # Test prompt
    test_prompt = "Explain what artificial intelligence is"
    
    print(f"\n📝 Test Prompt: '{test_prompt}'")
    print("-" * 50)
    
    # Test each style
    for style_name in chat_styles.keys():
        print(f"\n🎯 Style: '{style_name}'")
        print(f"   💭 Expected Tone: {chat_styles[style_name]['tone']}")
        
        try:
            # Create ChatDeepAI instance with specific style
            chat = ChatDeepAI(
                model="standard",
                chat_style=style_name
            )
            
            # Test the style (will get mock response since no API key)
            response = chat.invoke(HumanMessage(content=test_prompt))
            print(f"   🤖 Response: {response.content[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


def get_recommended_styles_by_use_case():
    """Get recommended chat styles organized by use case."""
    print("\n🎯 Recommended Chat Styles by Use Case")
    print("=" * 50)
    
    chat_styles = get_chat_styles()
    
    # Organize by use case
    use_cases = {}
    for style_name, style_info in chat_styles.items():
        best_for = style_info['best_for']
        if best_for not in use_cases:
            use_cases[best_for] = []
        use_cases[best_for].append({
            'style': style_name,
            'tone': style_info['tone'],
            'personality': style_info['personality']
        })
    
    for use_case, styles in use_cases.items():
        print(f"\n📋 {use_case.title()}:")
        for style_info in styles:
            print(f"   • '{style_info['style']}' - {style_info['tone']}")
    
    return use_cases


def quick_style_reference():
    """Quick reference guide for chat styles."""
    print("\n📚 Quick Chat Style Reference")
    print("=" * 40)
    
    styles = [
        ("chatgpt-alternative", "Default - General conversations"),
        ("ai-code", "Programming and technical discussions"),  
        ("mathematics", "Math problems and scientific discussions"),
        ("professional", "Business and formal communications"),
        ("creative", "Creative writing and artistic discussions"),
        ("casual", "Informal and friendly conversations"),
        ("goku", "Energetic and motivational"),
        ("gojo_9", "Confident and charismatic")
    ]
    
    print("\n🔤 Style Name → Use Case:")
    for style, use_case in styles:
        print(f"   '{style}' → {use_case}")


def code_examples():
    """Provide code examples for using different chat styles."""
    print("\n💻 Code Examples")
    print("=" * 20)
    
    examples = [
        {
            "title": "General Conversation",
            "style": "chatgpt-alternative",
            "code": '''chat = ChatDeepAI(chat_style="chatgpt-alternative")
response = chat.invoke("Hello, how are you?")'''
        },
        {
            "title": "Programming Help", 
            "style": "ai-code",
            "code": '''chat = ChatDeepAI(chat_style="ai-code")
response = chat.invoke("Write a Python function to sort a list")'''
        },
        {
            "title": "Math Problems",
            "style": "mathematics", 
            "code": '''chat = ChatDeepAI(chat_style="mathematics")
response = chat.invoke("Solve: 2x + 5 = 15")'''
        },
        {
            "title": "Business Communication",
            "style": "professional",
            "code": '''chat = ChatDeepAI(chat_style="professional")
response = chat.invoke("Draft a professional email")'''
        },
        {
            "title": "Creative Writing",
            "style": "creative",
            "code": '''chat = ChatDeepAI(chat_style="creative")
response = chat.invoke("Write a short story about space")'''
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['title']} (Style: '{example['style']}'):")
        print(f"```python\n{example['code']}\n```")


if __name__ == "__main__":
    print("🎨 LangChain-DeepAI Chat Styles Guide")
    print("=" * 50)
    
    # Main functions
    chat_styles = list_all_chat_styles()
    aliases = list_chat_style_aliases()
    
    # Demonstrations
    demonstrate_chat_styles()
    use_cases = get_recommended_styles_by_use_case()
    quick_style_reference()
    code_examples()
    
    # Summary
    print("\n📊 Summary")
    print("=" * 15)
    print(f"✅ Total Chat Styles: {len(chat_styles)}")
    print(f"✅ Available Aliases: {len(aliases)}")
    print(f"✅ Use Case Categories: {len(use_cases)}")
    print("\n🎉 All chat styles listed successfully!")
    
    # Quick API reference
    print("\n🔍 Quick API Reference:")
    print("```python")
    print("from langchain_deepai import ChatDeepAI, get_chat_styles")
    print("")
    print("# List all styles")
    print("styles = get_chat_styles()")
    print("print(list(styles.keys()))")
    print("")
    print("# Use a specific style")
    print("chat = ChatDeepAI(chat_style='your_preferred_style')")
    print("response = chat.invoke('Your message here')")
    print("```")
