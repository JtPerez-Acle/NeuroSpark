"""Data generator module for creating synthetic KQML messages and interactions."""
from datetime import datetime, timezone
import random
import uuid
from typing import Dict, List, Any, Optional

class DataGenerator:
    """Generate synthetic data for testing."""
    
    def __init__(self):
        """Initialize data generator with agent types and roles."""
        self.agent_types = {
            "sensor": ["temperature", "pressure", "humidity"],
            "analyzer": ["pattern", "anomaly", "trend"],
            "coordinator": ["system", "network", "process"],
            "actuator": ["hvac", "valve", "switch"]
        }
        
        self.performatives = {
            "sensor": ["tell", "inform"],
            "analyzer": ["evaluate", "inform"],
            "coordinator": ["achieve", "request"],
            "actuator": ["tell", "inform"]
        }

    def create_agent_profile(self, agent_type: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """Create a single agent profile."""
        if not agent_type:
            agent_type = random.choice(list(self.agent_types.keys()))
        if not role:
            role = random.choice(self.agent_types[agent_type])
            
        return {
            "id": str(uuid.uuid4()),
            "type": agent_type,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def create_agent_profiles(self, num_agents: int) -> List[Dict[str, Any]]:
        """Create multiple agent profiles."""
        return [self.create_agent_profile() for _ in range(num_agents)]

    def generate_content_by_type(self, agent_type: str, role: str) -> Dict[str, Any]:
        """Generate content based on agent type and role."""
        if agent_type == "sensor":
            reading = round(random.uniform(0, 100), 2)
            return {
                "reading": reading,
                role: reading,
                "celsius": reading if role == "temperature" else None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        elif agent_type == "analyzer":
            return {
                "analysis": f"{role}_analysis_{random.randint(1, 1000)}",
                "status": random.choice(["normal", "warning", "critical"]),
                "confidence": round(random.uniform(0, 1), 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        elif agent_type == "coordinator":
            return {
                "command": f"{role}_command_{random.randint(1, 1000)}",
                "action": random.choice(["start", "stop", "update"]),
                "priority": random.choice(["low", "medium", "high"]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        elif agent_type == "actuator":
            return {
                "status": random.choice(["active", "inactive", "error"]),
                "action_status": random.choice(["success", "pending", "failed"]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def get_performative_by_type(self, agent_type: str) -> str:
        """Get appropriate performative for agent type."""
        return random.choice(self.performatives[agent_type])

    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any], run_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate an interaction between two agents."""
        performative = self.get_performative_by_type(sender["type"])
        content = self.generate_content_by_type(sender["type"], sender["role"])
        
        # Create KQML message
        kqml_content = f"""(
            {performative}
            :sender {sender["id"]}
            :receiver {receiver["id"]}
            :content {str(content)}
            :language json
            :ontology {sender["type"]}_{sender["role"]}
        )"""
        
        # Create interaction data
        interaction = {
            "id": str(uuid.uuid4()),
            "source_id": sender["id"],
            "target_id": receiver["id"],
            "performative": performative,
            "content": content,
            "kqml_content": kqml_content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if run_id:
            interaction["run_id"] = run_id
            
        return interaction

    def generate_synthetic_data(self, num_agents: int, num_interactions: int) -> Dict[str, Any]:
        """Generate synthetic dataset with agents and interactions."""
        # Create agents
        agents = self.create_agent_profiles(num_agents)
        
        # Generate interactions
        interactions = []
        for _ in range(num_interactions):
            sender, receiver = random.sample(agents, 2)
            interaction = self.generate_interaction(sender, receiver)
            interactions.append(interaction)
        
        return {
            "agents": agents,
            "interactions": interactions
        }

    def generate_synthetic_kqml(self) -> Dict[str, Any]:
        """Generate a synthetic KQML message."""
        # Create two random agents
        sender = self.create_agent_profile()
        receiver = self.create_agent_profile()
        
        # Generate interaction between them
        interaction = self.generate_interaction(sender, receiver)
        
        # Return just the KQML-related parts
        return {
            "performative": interaction["performative"],
            "content": interaction["content"],
            "kqml_content": interaction["kqml_content"]
        }
