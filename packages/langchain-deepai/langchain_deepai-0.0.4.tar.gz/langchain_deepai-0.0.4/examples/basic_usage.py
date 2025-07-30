#!/usr/bin/env python3
"""
Basic usage examples for langchain-deepai package.

This example shows how to use the ChatDeepAI model with LangChain.
"""

import os
from langchain_deepai import ChatDeepAI
from langchain_core.messages import HumanMessage, SystemMessage

def example_with_api_key():
    """Example using API key directly."""
    print("=== Example 1: Using API key directly ===")
    
    # Replace with your actual API key
    api_key = "your-deepai-api-key-here"
    
    # Create the model
    chat = ChatDeepAI(
        api_key=api_key,
        model="standard", 
        chat_style="chatgpt-alternative"
    )
    
    # Create messages
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hello! What can you help me with?")
    ]
    
    try:
        # Generate response
        response = chat.invoke(messages)
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")
    print()


def example_with_environment_variable():
    """Example using environment variable."""
    print("=== Example 2: Using environment variable ===")
    
    # Set environment variable (you can also set this in your shell)
    # os.environ["DEEPAI_API_KEY"] = "your-deepai-api-key-here"
    
    # Create the model without API key - it will use env var
    chat = ChatDeepAI(
        model="standard",
        chat_style="chat"  # This will be mapped to "chatgpt-alternative"
    )
    
    # Create message
    message = HumanMessage(content="Explain what LangChain is in simple terms.")
    
    try:
        # Generate response
        response = chat.invoke([message])
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")
    print()


def example_set_api_key_later():
    """Example setting API key after initialization."""
    print("=== Example 3: Setting API key after initialization ===")
    
    # Create the model without API key
    chat = ChatDeepAI(
        model="standard",
        chat_style="professional"
    )
    
    # Set API key later
    chat.set_api_key("your-deepai-api-key-here")
    
    # Create message
    message = HumanMessage(content="What are the benefits of using AI in business?")
    
    try:
        # Generate response
        response = chat.invoke([message])
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")
    print()


def example_different_models_and_styles():
    """Example showing different models and chat styles."""
    print("=== Example 4: Different models and chat styles ===")
    
    # Set your API key
    api_key = "your-deepai-api-key-here"
    
    examples = [
        {"model": "standard", "style": "chatgpt-alternative", "prompt": "Tell me a joke"},
        {"model": "code", "style": "ai-code", "prompt": "Write a Python function to calculate fibonacci"},
        {"model": "math", "style": "mathematics", "prompt": "Explain the quadratic formula"},
        {"model": "standard", "style": "creative", "prompt": "Write a short poem about AI"},
    ]
    
    for example in examples:
        print(f"\nModel: {example['model']}, Style: {example['style']}")
        
        chat = ChatDeepAI(
            api_key=api_key,
            model=example['model'],
            chat_style=example['style']
        )
        
        message = HumanMessage(content=example['prompt'])
        
        try:
            response = chat.invoke([message])
            print(f"Response: {response.content[:200]}...")  # First 200 chars
        except Exception as e:
            print(f"Error: {e}")
    print()


def example_with_model_kwargs():
    """Example using additional model parameters."""
    print("=== Example 5: Using model kwargs ===")
    
    chat = ChatDeepAI(
        api_key="your-deepai-api-key-here",
        model="standard",
        chat_style="casual",
        max_tokens=100,  # Limit response length
        temperature=0.7,  # Control randomness
        model_kwargs={
            "custom_param": "value"  # Additional parameters
        }
    )
    
    message = HumanMessage(content="Explain quantum computing briefly.")
    
    try:
        response = chat.invoke([message])
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")
    print()


if __name__ == "__main__":
    print("LangChain DeepAI Basic Usage Examples")
    print("=====================================\n")
    
    print("Note: Replace 'your-deepai-api-key-here' with your actual API key")
    print("or set the DEEPAI_API_KEY environment variable.\n")
    
    # Run examples (comment out if you don't have an API key)
    # example_with_api_key()
    # example_with_environment_variable()
    # example_set_api_key_later()
    # example_different_models_and_styles()
    # example_with_model_kwargs()
    
    # Example without API key to show no errors during import/initialization
    print("=== Testing import and initialization (no API key needed) ===")
    try:
        chat = ChatDeepAI(model="standard", chat_style="chat")
        print("✅ ChatDeepAI imported and initialized successfully!")
        print(f"Model: {chat.model_name}")
        print(f"Chat style: {chat.chat_style}")
        print(f"LLM Type: {chat._llm_type}")
        print("\n✅ No errors during import/initialization!")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
