#!/usr/bin/env python3
"""Simple ArangoDB connection test script."""

import os
from arango import ArangoClient

def test_arango_connection():
    """Test direct connection to ArangoDB with the configured credentials."""
    host = os.getenv("ARANGO_HOST", "localhost")
    port = os.getenv("ARANGO_PORT", "8529")
    user = os.getenv("ARANGO_USER", "root")
    password = os.getenv("ARANGO_PASSWORD", "password")
    db_name = os.getenv("ARANGO_DB", "agent_interactions")
    
    url = f"http://{host}:{port}"
    print(f"Trying to connect to ArangoDB at: {url}")
    
    try:
        # Create a client
        client = ArangoClient(hosts=url)
        
        # Connect to _system database as root user (needed to create new database)
        sys_db = client.db("_system", username=user, password=password)
        
        # Check if our database exists
        if not sys_db.has_database(db_name):
            print(f"Database '{db_name}' does not exist. Creating it...")
            sys_db.create_database(
                name=db_name,
                users=[{"username": user, "password": password, "active": True}]
            )
            print(f"Database '{db_name}' created successfully")
        else:
            print(f"Database '{db_name}' already exists")
        
        # Connect to our database
        db = client.db(db_name, username=user, password=password)
        
        # Create test collection if it doesn't exist
        if not db.has_collection("test_collection"):
            print("Creating test collection...")
            test_collection = db.create_collection("test_collection")
            print("Test collection created")
        else:
            test_collection = db.collection("test_collection")
            print("Using existing test collection")
        
        # Insert a test document
        doc = {
            "_key": "test_doc",
            "name": "Connection Test",
            "created": True
        }
        
        # Check if the document already exists before inserting
        if not test_collection.has(doc["_key"]):
            print("Creating test document...")
            test_collection.insert(doc)
            print("Test document created successfully")
        else:
            print("Test document already exists")
        
        # Query the test document
        result = test_collection.get(doc["_key"])
        print(f"Retrieved test document: {result}")
        
        # Test AQL query
        print("Running AQL query...")
        cursor = db.aql.execute("FOR doc IN test_collection RETURN doc")
        docs = [document for document in cursor]
        print(f"Found {len(docs)} documents in test_collection")
        
        print("\nArangoDB connection test successful!")
        return True
        
    except Exception as e:
        print(f"Connection error: {e}")
        print("\n=== ArangoDB connection failed ===")
        print("1. Check if the ArangoDB container is running properly:")
        print("   docker-compose ps")
        print("2. Try accessing the ArangoDB UI at http://localhost:8529")
        print("3. You may need to restart the ArangoDB container:")
        print("   docker-compose down")
        print("   docker-compose up -d arangodb")
        return False

if __name__ == "__main__":
    test_arango_connection()