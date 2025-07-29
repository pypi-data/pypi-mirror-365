#!/usr/bin/env python3
"""
Complete example showing how to use langchain_g4f package
"""

from langchain_g4f import ChatG4F
import g4f

def main():
    print("🚀 LangChain G4F Example")
    print("=" * 40)
    
    # Create ChatG4F instance
    chat = ChatG4F(
        model="gpt-3.5-turbo",
        provider=None,  # Auto-select provider
        temperature=0.7,
    )
    
    print(f"Model: {chat.model_name}")
    print(f"Temperature: {chat.temperature}")
    print(f"Provider: {chat.provider}")
    
    # Example 1: Basic usage with g4f directly
    print("\n📝 Example 1: Basic G4F Usage")
    print("-" * 30)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ]
    
    try:
        # Use g4f directly with ChatG4F parameters
        response = g4f.ChatCompletion.create(
            model=chat.model_name,
            messages=messages,
            provider=chat.provider,
            temperature=chat.temperature,
        )
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error with basic usage: {e}")
    
    # Example 2: Try with LangChain (if available)
    print("\n🔗 Example 2: LangChain Integration")
    print("-" * 35)
    
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is the capital of France?")
        ]
        
        response = chat.invoke(messages)
        print(f"LangChain Response: {response.content}")
        
    except ImportError:
        print("LangChain core not available - install with: pip install langchain-core")
    except Exception as e:
        print(f"Error with LangChain integration: {e}")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()
