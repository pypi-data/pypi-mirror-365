#!/usr/bin/env python3
"""
Working example showing how to use langchain_g4f package with different providers
"""

from langchain_g4f import ChatG4F
import g4f

def test_providers():
    print("🚀 LangChain G4F Provider Testing")
    print("=" * 50)
    
    # List of providers to test
    providers_to_test = [
        ("Auto (g4f chooses)", None),
        ("Bing", g4f.Provider.Bing),
        ("DDG", g4f.Provider.DDG),
        ("FreeGpt", g4f.Provider.FreeGpt),
    ]
    
    for provider_name, provider in providers_to_test:
        print(f"\n🔍 Testing provider: {provider_name}")
        print("-" * 40)
        
        try:
            # Create ChatG4F instance
            chat = ChatG4F(
                model="gpt-3.5-turbo",
                provider=provider,
                temperature=0.7,
            )
            
            print(f"✅ ChatG4F instance created")
            print(f"   Model: {chat.model_name}")
            print(f"   Provider: {chat.provider}")
            
            # Try a simple request
            messages = [
                {"role": "user", "content": "Say 'Hello from g4f!' in one sentence."}
            ]
            
            response = g4f.ChatCompletion.create(
                model=chat.model_name,
                messages=messages,
                provider=chat.provider,
                temperature=chat.temperature,
            )
            
            print(f"   Response: {response}")
            break  # If successful, stop trying other providers
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print(f"\n🎉 Provider testing completed!")

def test_langchain_integration():
    print("\n🔗 Testing LangChain Integration")
    print("=" * 40)
    
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        
        # Create ChatG4F instance
        chat = ChatG4F(
            model="gpt-3.5-turbo",
            provider=None,  # Auto-select
            temperature=0.7,
        )
        
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is 2+2? Answer in one word.")
        ]
        
        response = chat.invoke(messages)
        print(f"✅ LangChain response: {response.content}")
        
    except ImportError:
        print("ℹ️  LangChain core not available")
        print("   Install with: pip install langchain-core")
    except Exception as e:
        print(f"❌ LangChain error: {e}")

if __name__ == "__main__":
    test_providers()
    test_langchain_integration()
