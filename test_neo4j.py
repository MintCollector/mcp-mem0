#!/usr/bin/env python3
"""
Test script to verify Neo4j connection independently
"""
import os
from dotenv import load_dotenv

def test_neo4j_connection():
    """Test direct connection to Neo4j"""
    print("🔍 Testing Neo4j connection...\n")
    
    # Load environment variables
    load_dotenv()
    
    try:
        from neo4j import GraphDatabase
        
        # Get Neo4j configuration
        neo4j_url = os.getenv('NEO4J_URL')
        neo4j_username = os.getenv('NEO4J_USERNAME')
        neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        if not all([neo4j_url, neo4j_username, neo4j_password]):
            print("❌ Neo4j credentials not found in environment variables!")
            print("   Please ensure NEO4J_URL, NEO4J_USERNAME, and NEO4J_PASSWORD are set in .env")
            return False
        
        print(f"📍 Connecting to Neo4j:")
        print(f"   URL: {neo4j_url}")
        print(f"   Username: {neo4j_username}")
        print(f"   Password: {'*' * len(neo4j_password)}\n")
        
        # Create driver
        print("🔗 Creating Neo4j driver...")
        driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_username, neo4j_password))
        
        # Test connection
        print("🔗 Testing connection...")
        with driver.session() as session:
            # Simple query to test connection
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"✅ Successfully connected to Neo4j!")
            print(f"   Response: {record['message']}\n")
            
            # Get Neo4j version
            version_result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in version_result:
                if record["name"] == "Neo4j Kernel":
                    print(f"📊 Neo4j Info:")
                    print(f"   - Version: {record['versions'][0]}")
                    print(f"   - Edition: {record['edition']}")
                    break
            
            # Count existing nodes and relationships
            print(f"\n📈 Database statistics:")
            
            # Count nodes
            node_result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = node_result.single()["node_count"]
            print(f"   - Nodes: {node_count}")
            
            # Count relationships
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = rel_result.single()["rel_count"]
            print(f"   - Relationships: {rel_count}")
            
            # Show node labels if any exist
            if node_count > 0:
                labels_result = session.run("CALL db.labels()")
                labels = [record["label"] for record in labels_result]
                if labels:
                    print(f"   - Node labels: {', '.join(labels[:5])}")
                    if len(labels) > 5:
                        print(f"     ... and {len(labels) - 5} more")
        
        driver.close()
        return True
        
    except ImportError:
        print("❌ neo4j driver not installed!")
        print("   Install with: uv pip install neo4j")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Neo4j: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Common error hints
        if "authentication" in str(e).lower():
            print("   💡 Check your username/password")
        elif "connection" in str(e).lower() or "resolve" in str(e).lower():
            print("   💡 Check your Neo4j URL and ensure Neo4j is running")
        elif "certificate" in str(e).lower():
            print("   💡 For local Neo4j, try 'bolt://' instead of 'neo4j+s://'")
        
        return False

if __name__ == "__main__":
    print("📋 Neo4j Connection Test")
    print("=" * 40)
    
    success = test_neo4j_connection()
    
    if success:
        print("\n🎉 Neo4j connection test successful!")
    else:
        print("\n❌ Neo4j connection test failed!")