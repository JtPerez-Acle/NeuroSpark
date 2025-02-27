#!/usr/bin/env python3
"""
Complex test script to verify ArangoDB persistence with multiple interactions
"""

import asyncio
import json
import uuid
from datetime import datetime
import os
import random
from app.database import create_database
from loguru import logger

async def test_complex_persistence():
    """Test database with multiple interactions and agents"""
    
    print('Connecting to database...')
    db = await create_database()
    print(f'Connected: {db.is_connected()}')
    
    try:
        # Clean start
        print("Clearing database...")
        await db.clear_database()
        
        # 1. Create multiple agents with randomized IDs
        agents = []
        for i in range(5):
            agent_id = f"test_agent_{i}_{uuid.uuid4().hex[:8]}".replace('-', '_')
            agent_type = random.choice(["human", "ai", "system"])
            agent_role = random.choice(["user", "assistant", "observer"])
            
            agent_data = {
                "id": agent_id,
                "type": agent_type,
                "role": agent_role,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"Storing agent: {agent_id} ({agent_type}/{agent_role})")
            await db.store_agent(agent_data)
            agents.append(agent_data)
        
        # 2. Verify agents were stored
        stored_agents = await db.get_agents()
        print(f"Found {len(stored_agents)} agents")
        for agent in stored_agents:
            print(f"Agent: {agent['id']} ({agent['type']}/{agent['role']})")
        
        # 3. Create interactions between agents
        interactions = []
        for i in range(10):
            # Select random sender and receiver (possibly the same)
            sender = random.choice(agents)
            receiver = random.choice(agents)
            
            interaction_id = f"test_interaction_{i}_{uuid.uuid4().hex[:8]}".replace('-', '_')
            interaction_data = {
                "id": interaction_id,
                "sender_id": sender["id"],
                "receiver_id": receiver["id"],
                "topic": f"test_topic_{i}",
                "message": f"Test message {i} from {sender['id']} to {receiver['id']}",
                "interaction_type": random.choice(["message", "command", "query", "response"]),
                "timestamp": datetime.now().isoformat(),
                "priority": random.randint(1, 5),
                "sentiment": round(random.uniform(-1.0, 1.0), 2)
            }
            
            print(f"Storing interaction: {interaction_id}")
            await db.store_interaction(interaction_data)
            interactions.append(interaction_data)
        
        # 4. Verify interactions were stored
        stored_interactions = await db.get_interactions()
        print(f"Found {len(stored_interactions)} interactions")
        for interaction in stored_interactions:
            print(f"Interaction: {interaction.get('id')} from {interaction['sender_id']} to {interaction['receiver_id']}")
        
        # 5. Test querying agent interactions
        agent_id = agents[0]["id"]
        agent_interactions = await db.get_agent_interactions(agent_id)
        print(f"\nFound {len(agent_interactions)} interactions for agent {agent_id}")
        
        # 6. Test retrieving a specific interaction
        if stored_interactions:
            interaction_id = stored_interactions[0]["id"]
            specific_interaction = await db.get_interaction(interaction_id)
            print(f"\nRetrieved interaction {interaction_id}:")
            print(f"  From: {specific_interaction['sender_id']}")
            print(f"  To: {specific_interaction['receiver_id']}")
            print(f"  Message: {specific_interaction['message']}")
        
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
    asyncio.run(test_complex_persistence())