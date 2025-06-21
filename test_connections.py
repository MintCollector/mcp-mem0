#!/usr/bin/env python3
"""
Test script to verify both Qdrant and Neo4j connections independently
"""
import os
import sys
from dotenv import load_dotenv

# Import the individual test functions
try:
    from test_qdrant import test_qdrant_connection
    from test_neo4j import test_neo4j_connection
    from test_llm import test_llm_setup
except ImportError:
    print("❌ Could not import test modules. Make sure test_qdrant.py, test_neo4j.py, and test_llm.py exist.")
    sys.exit(1)

def main():
    """Run all connection tests"""
    print("🧪 System Component Tests")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    results = {}
    
    # Test LLM
    print("\n1️⃣  LLM TEST")
    print("-" * 20)
    results['llm'] = test_llm_setup()
    
    # Test Qdrant
    print("\n\n2️⃣  QDRANT TEST")
    print("-" * 20)
    results['qdrant'] = test_qdrant_connection()
    
    # Test Neo4j
    print("\n\n3️⃣  NEO4J TEST")
    print("-" * 20)
    results['neo4j'] = test_neo4j_connection()
    
    # Summary
    print("\n\n📊 TEST SUMMARY")
    print("=" * 50)
    
    for service, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{service.upper():.<20} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All connection tests passed!")
        print("   You can now test the full Mem0 integration.")
    else:
        failed_services = [service for service, success in results.items() if not success]
        print(f"\n⚠️  Some tests failed: {', '.join(failed_services)}")
        print("   Please fix the failing connections before proceeding.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)