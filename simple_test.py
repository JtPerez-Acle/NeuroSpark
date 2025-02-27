#!/usr/bin/env python3
"""
Simple test script to verify ArangoDB persistence with basic operations
"""

import asyncio
import json
import uuid
from datetime import datetime
import os
from app.database import create_database
from loguru import logger

async def test_simple_persistence():
    """Test basic database operations"""
    
    print('Connecting to database...')
    db = await create_database()
    print(f'Connected: {db.is_connected()}')
    
    try:
        # Clean start
        print("Clearing database...")
        await db.clear_database()
        
        # 1. Create and store a simple agent
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}".replace('-', '_')
        agent_data = {
            "id": agent_id,
            "type": "test",
            "role": "tester",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Storing agent: {agent_id}")
        await db.store_agent(agent_data)
        
        # 2. Verify agent was stored
        agents = await db.get_agents()
        print(f"Found {len(agents)} agents")
        for agent in agents:
            print(f"Agent: {agent['id']} ({agent['type']}/{agent['role']})")
        
        # 3. Create and store a test interaction
        interaction_id = f"test_interaction_{uuid.uuid4().hex[:8]}".replace('-', '_')
        interaction_data = {
            "id": interaction_id,
            "sender_id": agent_id,
            "receiver_id": agent_id,  # self interaction for simplicity
            "topic": "test_topic",
            "message": "Test message",
            "interaction_type": "test",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Storing interaction: {interaction_id}")
        await db.store_interaction(interaction_data)
        
        # 4. Verify interaction was stored
        interactions = await db.get_interactions()
        print(f"Found {len(interactions)} interactions")
        for interaction in interactions:
            print(f"Interaction: {interaction.get('id')} from {interaction['sender_id']} to {interaction['receiver_id']}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await db.disconnect()
        print('Disconnected from database')

if __name__ == "__main__":
    # Set environment variables
    os.environ["ARANGO_HOST"] = "localhost"
    os.environ["ARANGO_PORT"] = "8529"
    os.environ["ARANGO_USER"] = "root"
    os.environ["ARANGO_PASSWORD"] = "password"
    os.environ["ARANGO_DB"] = "agent_interactions"
    
    # Run the test
    asyncio.run(test_simple_persistence())