"""Agent interaction handling module."""
from datetime import datetime
import json
from loguru import logger
from typing import Dict, Any, Optional
import uuid

from app.models import AgentInteraction

async def process_interaction(interaction_data: Dict[str, Any]) -> AgentInteraction:
    """Process an agent interaction."""
    start_time = datetime.now()
    
    try:
        # If duration_ms is not provided, we'll calculate it at the end
        calculate_duration = "duration_ms" not in interaction_data
        
        # Create an AgentInteraction object from the data
        interaction = AgentInteraction(**interaction_data)
        
        # Calculate processing time if needed
        if calculate_duration:
            process_time = (datetime.now() - start_time).total_seconds() * 1000
            interaction.duration_ms = int(process_time)
        
        logger.info(
            "Successfully processed agent interaction",
            extra={
                "type": "interaction",
                "data": {
                    "interaction_id": interaction.interaction_id,
                    "sender_id": interaction.sender_id,
                    "receiver_id": interaction.receiver_id,
                    "topic": interaction.topic,
                    "interaction_type": interaction.interaction_type,
                    "duration_ms": interaction.duration_ms
                }
            }
        )
        
        return interaction
    
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.exception(
            "Failed to process agent interaction",
            extra={
                "type": "interaction",
                "data": {
                    "raw_data": interaction_data,
                    "error": str(e),
                    "process_time_ms": process_time
                }
            }
        )
        raise

def generate_synthetic_interaction(
    sender_id: str,
    receiver_id: str,
    topic: str,
    message: str,
    interaction_type: Optional[str] = "message",
    priority: Optional[int] = None,
    run_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate synthetic interaction data for testing."""
    
    # Create an ArangoDB-friendly ID
    interaction_id = str(uuid.uuid4()).replace('-', '_')
    
    return {
        "interaction_id": interaction_id,
        "timestamp": datetime.now().isoformat(),
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "topic": topic,
        "message": message,
        "interaction_type": interaction_type,
        "priority": priority,
        "run_id": run_id,
        "metadata": {
            "synthetic": True,
            "generated_at": datetime.now().isoformat()
        }
    }

# Example usage
if __name__ == "__main__":
    # Generate a synthetic interaction
    synthetic_data = generate_synthetic_interaction(
        sender_id="agent1",
        receiver_id="agent2",
        topic="temperature",
        message="Current temperature is 25°C",
        interaction_type="report",
        priority=3
    )
    
    print(f"Synthetic interaction: {json.dumps(synthetic_data, indent=2)}")
    
    # Process the synthetic interaction
    import asyncio
    
    async def test_process():
        interaction = await process_interaction(synthetic_data)
        print(f"Processed interaction: {interaction.json(indent=2)}")
    
    asyncio.run(test_process())