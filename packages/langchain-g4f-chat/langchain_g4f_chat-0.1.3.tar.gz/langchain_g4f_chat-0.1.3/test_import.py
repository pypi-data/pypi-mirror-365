#!/usr/bin/env python3
"""
Test script to verify langchain_g4f import and basic functionality
"""

try:
    from langchain_g4f import ChatG4F
    print("✅ ChatG4F import successful!")
    
    import g4f
    print("✅ g4f import successful!")
    
    # Create a ChatG4F instance
    chat = ChatG4F(
        model="gpt-3.5-turbo",
        provider=None,  # Auto-select provider
        temperature=0.7,
    )
    print("✅ ChatG4F instance created successfully!")
    
    # Test basic configuration
    print(f"Model: {chat.model_name}")
    print(f"Temperature: {chat.temperature}")
    print(f"Provider: {chat.provider}")
    
    print("\n🎉 All imports and basic functionality working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
