#!/usr/bin/env python3
"""
Test script to verify LLM setup (OpenAI client with Gemini backend)
"""
import os
from dotenv import load_dotenv

def test_llm_setup():
    """Test the LLM configuration using OpenAI client"""
    print("🔍 Testing LLM setup...\n")
    
    # Load environment variables
    load_dotenv()
    
    try:
        from openai import OpenAI
        
        # Get LLM configuration
        llm_provider = os.getenv('LLM_PROVIDER')
        llm_base_url = os.getenv('LLM_BASE_URL')
        llm_api_key = os.getenv('LLM_API_KEY')
        llm_model = os.getenv('LLM_CHOICE')
        embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
        
        if not all([llm_provider, llm_base_url, llm_api_key, llm_model]):
            print("❌ Missing required LLM environment variables!")
            missing = [var for var, val in [
                ('LLM_PROVIDER', llm_provider),
                ('LLM_BASE_URL', llm_base_url), 
                ('LLM_API_KEY', llm_api_key),
                ('LLM_CHOICE', llm_model)
            ] if not val]
            print(f"   Missing: {', '.join(missing)}")
            return False
        
        print(f"📍 LLM Configuration:")
        print(f"   Provider: {llm_provider}")
        print(f"   Base URL: {llm_base_url}")
        print(f"   Model: {llm_model}")
        print(f"   Embedding Model: {embedding_model}")
        print(f"   API Key: {'✓ Set' if llm_api_key else '✗ Not set'}\n")
        
        # Initialize OpenAI client with custom base URL
        print("🔗 Initializing OpenAI client...")
        client = OpenAI(
            api_key=llm_api_key,
            base_url=llm_base_url
        )
        print("✅ OpenAI client initialized successfully!\n")
        
        # Test 1: Simple chat completion
        print("💬 Test 1: Simple chat completion...")
        try:
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "user", "content": "Hello! Please respond with exactly 'Test successful' if you can understand this message."}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            message = response.choices[0].message.content
            print(f"✅ Chat completion successful!")
            print(f"   Response: {message}")
            
            if "test successful" in message.lower():
                print("✅ Model is responding correctly!")
            else:
                print("⚠️  Model response unexpected, but connection works")
            
        except Exception as e:
            print(f"❌ Chat completion failed: {e}")
            return False
        
        # Test 2: Test embeddings
        print(f"\n🔤 Test 2: Testing embeddings with {embedding_model}...")
        try:
            # For Gemini/Google AI, embeddings might not be available through OpenAI endpoint
            # Let's test if it works, but handle gracefully if it doesn't
            embedding_response = client.embeddings.create(
                model=embedding_model,
                input="This is a test sentence for embedding generation."
            )
            
            embedding = embedding_response.data[0].embedding
            print(f"✅ Embedding generation successful!")
            print(f"   Embedding dimensions: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
            
        except Exception as e:
            print(f"⚠️  Embedding test failed: {e}")
            print("   This might be expected if using Gemini through OpenAI endpoint")
            print("   Embeddings might need to be handled differently for Gemini")
            
            # Check if this is a Gemini setup
            if "generativelanguage.googleapis.com" in llm_base_url:
                print("   💡 Detected Google AI Studio/Gemini setup")
                print("   💡 Consider using Google's embedding API directly for embeddings")
        
        # Test 3: Test with system message
        print(f"\n🎭 Test 3: Testing with system message...")
        try:
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always responds in a friendly manner."},
                    {"role": "user", "content": "What's 2+2?"}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            message = response.choices[0].message.content
            print(f"✅ System message test successful!")
            print(f"   Response: {message}")
            
        except Exception as e:
            print(f"❌ System message test failed: {e}")
            return False
        
        # Test 4: Test temperature and parameters
        print(f"\n🌡️  Test 4: Testing model parameters...")
        try:
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "user", "content": "Generate a creative short story title about space exploration."}
                ],
                max_tokens=50,
                temperature=0.8,  # Higher temperature for creativity
                top_p=0.9
            )
            
            message = response.choices[0].message.content
            print(f"✅ Parameter test successful!")
            print(f"   Creative response: {message}")
            
        except Exception as e:
            print(f"❌ Parameter test failed: {e}")
            return False
        
        return True
        
    except ImportError:
        print("❌ OpenAI library not installed!")
        print("   Install with: uv pip install openai")
        return False
    except Exception as e:
        print(f"❌ Error during LLM testing: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Common error hints
        if "authentication" in str(e).lower() or "401" in str(e):
            print("   💡 Check your API key")
        elif "connection" in str(e).lower() or "resolve" in str(e).lower():
            print("   💡 Check your base URL and internet connection")
        elif "model" in str(e).lower():
            print("   💡 Check if the model name is correct for your provider")
        
        return False

def test_mem0_llm_integration():
    """Test how the LLM setup works with our Mem0 configuration"""
    print(f"\n🔧 Testing LLM integration with Mem0 utils...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from utils import get_mem0_client
        
        # This will test if our utils.py correctly configures the LLM
        print("   Initializing Mem0 client with LLM configuration...")
        m = get_mem0_client()
        print("✅ Mem0 client with LLM integration successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Mem0 LLM integration failed: {e}")
        return False

if __name__ == "__main__":
    print("📋 LLM Setup Test")
    print("=" * 40)
    
    # Test basic LLM setup
    llm_success = test_llm_setup()
    
    # Test Mem0 integration
    integration_success = test_mem0_llm_integration()
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 40)
    print(f"LLM Setup........... {'✅ PASS' if llm_success else '❌ FAIL'}")
    print(f"Mem0 Integration.... {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if llm_success and integration_success:
        print("\n🎉 LLM setup is working correctly!")
        print("   Ready for Mem0 memory operations!")
    else:
        print("\n❌ LLM setup has issues. Please fix before proceeding.")