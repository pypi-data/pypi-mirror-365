"""
Basic usage examples for LangChain DeepAI integration.

This script demonstrates the fundamental features of the langchain-deepai package.
"""

import os
from langchain_deepai import ChatDeepAI, DeepAIMath, DeepAICode
from langchain_core.messages import HumanMessage, SystemMessage

def basic_chat_example():
    """Basic chat conversation example."""
    print("=== Basic Chat Example ===")
    
    # Initialize the chat model
    chat = ChatDeepAI(
        # api_key="your-api-key",  # Or set DEEPAI_API_KEY environment variable
        model_name="standard",
        chat_style="chatgpt-alternative"
    )
    
    # Single message
    messages = [HumanMessage(content="Hello! Tell me about artificial intelligence.")]
    response = chat.invoke(messages)
    print(f"Response: {response.content}")
    
    # Conversation with system message
    messages = [
        SystemMessage(content="You are a helpful assistant that explains complex topics simply."),
        HumanMessage(content="Explain quantum computing in simple terms.")
    ]
    response = chat.invoke(messages)
    print(f"Response: {response.content}")


def specialized_models_example():
    """Examples using specialized models."""
    print("\n=== Specialized Models Example ===")
    
    # Math model
    print("Math Model:")
    math_chat = DeepAIMath()
    math_response = math_chat.invoke([
        HumanMessage(content="Solve the quadratic equation: x² - 5x + 6 = 0")
    ])
    print(f"Math Response: {math_response.content}")
    
    # Code model
    print("\nCode Model:")
    code_chat = DeepAICode()
    code_response = code_chat.invoke([
        HumanMessage(content="Write a Python function to calculate fibonacci sequence")
    ])
    print(f"Code Response: {code_response.content}")


def chat_styles_example():
    """Examples of different chat styles."""
    print("\n=== Chat Styles Example ===")
    
    question = "How can I improve my productivity?"
    
    # Professional style
    professional_chat = ChatDeepAI(chat_style="professional")
    prof_response = professional_chat.invoke([HumanMessage(content=question)])
    print(f"Professional: {prof_response.content[:100]}...")
    
    # Casual style
    casual_chat = ChatDeepAI(chat_style="casual")
    casual_response = casual_chat.invoke([HumanMessage(content=question)])
    print(f"Casual: {casual_response.content[:100]}...")
    
    # Creative style
    creative_chat = ChatDeepAI(chat_style="creative")
    creative_response = creative_chat.invoke([HumanMessage(content=question)])
    print(f"Creative: {creative_response.content[:100]}...")


def session_management_example():
    """Example of session-based conversation."""
    print("\n=== Session Management Example ===")
    
    chat = ChatDeepAI()
    
    # Set a session ID for context
    chat.set_session_id("user-session-123")
    
    # First message
    response1 = chat.invoke([HumanMessage(content="My name is Alice and I love coding.")])
    print(f"Response 1: {response1.content}")
    
    # Second message - should remember context
    response2 = chat.invoke([HumanMessage(content="What's my name and what do I love?")])
    print(f"Response 2: {response2.content}")
    
    # Clear session
    chat.clear_session()


def model_information_example():
    """Example showing how to get model information."""
    print("\n=== Model Information Example ===")
    
    chat = ChatDeepAI()
    
    # Get available models
    models = chat.get_available_models()
    print("Available Models:")
    for model_name, info in models.items():
        print(f"  {model_name}: {info['description']}")
    
    # Get available chat styles
    styles = chat.get_available_chat_styles()
    print("\nAvailable Chat Styles:")
    for style_name, info in styles.items():
        print(f"  {style_name}: {info['description']}")


def main():
    """Run all examples."""
    print("LangChain DeepAI - Basic Usage Examples")
    print("=" * 50)
    
    try:
        basic_chat_example()
        specialized_models_example()
        chat_styles_example()
        session_management_example()
        model_information_example()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have set your DEEPAI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
