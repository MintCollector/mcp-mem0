#!/usr/bin/env python3
"""
Test script to verify Qdrant connection independently
"""
import os
from dotenv import load_dotenv

def test_qdrant_connection():
    """Test direct connection to Qdrant"""
    print("🔍 Testing Qdrant connection...\n")
    
    # Load environment variables
    load_dotenv()
    
    try:
        from qdrant_client import QdrantClient
        
        # Get Qdrant configuration
        qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
        qdrant_api_key = os.getenv('QDRANT_API_KEY')
        collection_name = os.getenv('QDRANT_COLLECTION', 'james_general')
        
        print(f"📍 Connecting to Qdrant:")
        if qdrant_host.startswith('https://'):
            print(f"   URL: {qdrant_host}")
            print(f"   API Key: {'✓ Set' if qdrant_api_key else '✗ Not set'}")
            
            # For cloud instances
            client = QdrantClient(
                url=qdrant_host,
                api_key=qdrant_api_key
            )
        else:
            print(f"   Host: {qdrant_host}")
            print(f"   Port: {qdrant_port}")
            
            # For local instances
            client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        print(f"   Collection: {collection_name}\n")
        
        # Test connection
        print("🔗 Testing connection...")
        collections = client.get_collections()
        print("✅ Successfully connected to Qdrant!")
        print(f"📋 Found {len(collections.collections)} collections:\n")
        
        for collection in collections.collections:
            print(f"   - {collection.name}")
            if collection.name == collection_name:
                print(f"     ✅ Target collection '{collection_name}' exists!")
        
        # Check if target collection exists
        collection_exists = any(c.name == collection_name for c in collections.collections)
        if not collection_exists:
            print(f"\n⚠️  Collection '{collection_name}' doesn't exist yet.")
            print("   It will be created automatically when first used.")
        
        # Get collection info if it exists
        if collection_exists:
            try:
                collection_info = client.get_collection(collection_name)
                print(f"\n📊 Collection '{collection_name}' info:")
                print(f"   - Vectors count: {collection_info.vectors_count}")
                print(f"   - Points count: {collection_info.points_count}")
            except Exception as e:
                print(f"   Could not get collection info: {e}")
        
        return True
        
    except ImportError:
        print("❌ qdrant-client not installed!")
        print("   Install with: uv pip install qdrant-client")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("📋 Qdrant Connection Test")
    print("=" * 40)
    
    success = test_qdrant_connection()
    
    if success:
        print("\n🎉 Qdrant connection test successful!")
    else:
        print("\n❌ Qdrant connection test failed!")