"""Data generator module for creating synthetic agent interactions."""
from datetime import datetime, timezone
import random
import uuid
from typing import Dict, List, Any, Optional

from app.kqml_handler import generate_synthetic_interaction

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
        
        self.interaction_types = {
            "sensor": ["report", "notification", "update"],
            "analyzer": ["query", "report", "alert"],
            "coordinator": ["command", "request", "broadcast"],
            "actuator": ["response", "update", "notification"]
        }
        
        self.topics = {
            "temperature": ["temperature_reading", "thermal_status", "heat_alert"],
            "pressure": ["pressure_reading", "pressure_change", "valve_status"],
            "humidity": ["humidity_level", "moisture_alert", "saturation_warning"],
            "pattern": ["pattern_detection", "anomaly_identification", "trend_analysis"],
            "anomaly": ["anomaly_detection", "outlier_report", "deviation_alert"],
            "trend": ["trend_forecast", "pattern_evolution", "historical_analysis"],
            "system": ["system_status", "resource_allocation", "performance_metrics"],
            "network": ["network_traffic", "connectivity_status", "bandwidth_utilization"],
            "process": ["process_monitoring", "task_allocation", "execution_status"],
            "hvac": ["temperature_control", "fan_speed", "operating_mode"],
            "valve": ["valve_position", "flow_rate", "pressure_regulation"],
            "switch": ["switch_status", "power_state", "circuit_control"]
        }
        
    def random_int(self, min_val: int, max_val: int) -> int:
        """Generate a random integer between min and max values."""
        return random.randint(min_val, max_val)
        
    def random_float(self, min_val: float, max_val: float) -> float:
        """Generate a random float between min and max values."""
        return min_val + random.random() * (max_val - min_val)

    def create_agent_profile(self, agent_type: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """Create a single agent profile."""
        if not agent_type:
            agent_type = random.choice(list(self.agent_types.keys()))
        if not role:
            role = random.choice(self.agent_types[agent_type])
            
        return {
            "id": str(uuid.uuid4()).replace('-', '_'),
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

    def get_interaction_type_by_agent(self, agent_type: str) -> str:
        """Get appropriate interaction type for agent type."""
        return random.choice(self.interaction_types[agent_type])
        
    def get_topic_by_role(self, role: str) -> str:
        """Get appropriate topic for agent role."""
        if role in self.topics:
            return random.choice(self.topics[role])
        else:
            # Default topics if role not found
            return random.choice(["status_update", "general_message", "system_notification"])

    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any], run_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate an interaction between two agents."""
        interaction_type = self.get_interaction_type_by_agent(sender["type"])
        topic = self.get_topic_by_role(sender["role"])
        content = self.generate_content_by_type(sender["type"], sender["role"])
        
        # Convert content dict to a readable message
        if sender["type"] == "sensor":
            message = f"Reading: {content.get('reading')} {sender['role']}"
        elif sender["type"] == "analyzer":
            message = f"Analysis: {content.get('status')} with {content.get('confidence', 0)*100:.0f}% confidence"
        elif sender["type"] == "coordinator":
            message = f"Command: {content.get('action')} with {content.get('priority', 'normal')} priority"
        elif sender["type"] == "actuator":
            message = f"Status: {content.get('status')} - Action {content.get('action_status', 'unknown')}"
        else:
            message = str(content)
        
        # Set priority based on content if available
        priority = None
        if "priority" in content:
            priority_map = {"low": 1, "medium": 3, "high": 5}
            priority = priority_map.get(content["priority"], 3)
        
        # Create interaction data using our new function
        interaction_data = generate_synthetic_interaction(
            sender_id=sender["id"],
            receiver_id=receiver["id"],
            topic=topic,
            message=message,
            interaction_type=interaction_type,
            priority=priority,
            run_id=run_id
        )
        
        return interaction_data

    def generate_synthetic_data(self, num_agents: int, num_interactions: int) -> Dict[str, Any]:
        """Generate synthetic dataset with agents and interactions."""
        # Create agents
        agents = self.create_agent_profiles(num_agents)
        
        # Create a run ID for all interactions
        run_id = str(uuid.uuid4()).replace('-', '_')
        
        # Generate interactions
        interactions = []
        for _ in range(num_interactions):
            sender, receiver = random.sample(agents, 2)
            interaction = self.generate_interaction(sender, receiver, run_id=run_id)
            interactions.append(interaction)
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id
        }

    def generate_synthetic_interaction_data(self) -> Dict[str, Any]:
        """Generate a synthetic agent interaction."""
        # Create two random agents
        sender = self.create_agent_profile()
        receiver = self.create_agent_profile()
        
        # Generate interaction between them
        interaction = self.generate_interaction(sender, receiver)
        
        return interaction
