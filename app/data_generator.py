"""Module for generating synthetic KQML data."""
import random
from datetime import datetime, timedelta, timezone
import uuid
from typing import List, Dict, Any
from .kqml_handler import KQMLMessage

class AgentProfile:
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities

class DataGenerator:
    """Class for generating synthetic KQML data."""
    
    def __init__(self):
        """Initialize the data generator."""
        self.agent_profiles = self.create_agent_profiles()
    
    def create_agent_profiles(self) -> List[Dict[str, str]]:
        """Create a list of agent profiles with predefined roles."""
        return [
            {"id": "sensor1", "role": "temperature_sensor"},
            {"id": "sensor2", "role": "humidity_sensor"},
            {"id": "analyzer1", "role": "data_analyzer"},
            {"id": "coordinator1", "role": "coordinator"},
            {"id": "actuator1", "role": "hvac_actuator"},
            {"id": "actuator2", "role": "light_actuator"},
            {"id": "actuator3", "role": "ventilation_actuator"}
        ]
    
    async def generate_measurement(self) -> Dict[str, str]:
        """Generate a measurement message from a sensor."""
        sensor = random.choice([p for p in self.agent_profiles if "sensor" in p["role"]])
        analyzer = random.choice([p for p in self.agent_profiles if "analyzer" in p["role"]])
        
        if "temperature" in sensor["role"]:
            value = round(random.uniform(18.0, 28.0), 1)
            unit = "celsius"
        else:
            value = round(random.uniform(30.0, 70.0), 1)
            unit = "percent"
        
        content = f"{value} {unit}"
        return {
            "sender": sensor["id"],
            "receiver": analyzer["id"],
            "performative": "tell",
            "content": content
        }
    
    async def generate_analysis_result(self) -> Dict[str, str]:
        """Generate an analysis result message."""
        analyzer = random.choice([p for p in self.agent_profiles if "analyzer" in p["role"]])
        coordinator = random.choice([p for p in self.agent_profiles if "coordinator" in p["role"]])
        
        status = random.choice(["normal", "warning", "critical"])
        content = f"status {status}"
        return {
            "sender": analyzer["id"],
            "receiver": coordinator["id"],
            "performative": "inform",
            "content": content
        }
    
    async def generate_action_result(self) -> Dict[str, str]:
        """Generate an action result message."""
        actuator = random.choice([p for p in self.agent_profiles if "actuator" in p["role"]])
        coordinator = random.choice([p for p in self.agent_profiles if "coordinator" in p["role"]])
        
        success = random.choice([True, False])
        if "hvac" in actuator["role"]:
            action = "temperature_adjustment"
        elif "light" in actuator["role"]:
            action = "light_adjustment"
        else:
            action = "ventilation_adjustment"
        
        content = f"action_complete {action} {str(success).lower()}"
        return {
            "sender": actuator["id"],
            "receiver": coordinator["id"],
            "performative": "tell",
            "content": content
        }
    
    async def generate_coordinator_message(self) -> Dict[str, str]:
        """Generate a coordinator message."""
        coordinator = random.choice([p for p in self.agent_profiles if "coordinator" in p["role"]])
        actuator = random.choice([p for p in self.agent_profiles if "actuator" in p["role"]])
        
        if "hvac" in actuator["role"]:
            value = round(random.uniform(19.0, 25.0), 1)
            content = f"set_temperature {value}"
        elif "light" in actuator["role"]:
            value = round(random.uniform(0, 100), 0)
            content = f"set_light_level {value}"
        else:
            value = round(random.uniform(0, 100), 0)
            content = f"set_ventilation {value}"
        
        return {
            "sender": coordinator["id"],
            "receiver": actuator["id"],
            "performative": "request",
            "content": content
        }
    
    async def generate_interaction(self, agents: List[Dict[str, str]] = None, run_id: str = None) -> Dict[str, Any]:
        """Generate a random interaction between agents."""
        if agents is None:
            agents = self.agent_profiles
        
        generators = [
            self.generate_measurement,
            self.generate_analysis_result,
            self.generate_action_result,
            self.generate_coordinator_message
        ]
        message = await random.choice(generators)()
        message["timestamp"] = datetime.now(timezone.utc).isoformat()
        message_id = str(uuid.uuid4())
        message["id"] = message_id
        message["message_id"] = message_id
        if run_id is not None:
            message["run_id"] = run_id
        return message
    
    async def generate_synthetic_kqml(self) -> Dict[str, Any]:
        """Generate a synthetic KQML message."""
        run_id = str(uuid.uuid4())
        message = await self.generate_interaction(
            agents=[{"id": "sensor1", "type": "sensor"}, {"id": "analyzer1", "type": "analyzer"}],
            run_id=run_id
        )
        message["run_id"] = run_id
        return message
    
    async def generate_synthetic_data(self, num_agents: int = 3, num_messages: int = 5) -> Dict[str, Any]:
        """Generate synthetic dataset with agents and interactions."""
        # Create agent profiles
        agents = []
        if num_agents > 0:
            agents.append({"id": "sensor1", "type": "sensor"})  # Always include sensor1
            for i in range(1, num_agents):
                agent_id = f"agent{i}"
                agent_type = random.choice(["sensor", "analyzer", "controller"])
                agents.append({"id": agent_id, "type": agent_type})
        
        # Generate interactions
        interactions = []
        run_id = str(uuid.uuid4())
        for _ in range(num_messages):
            interaction = await self.generate_interaction(agents, run_id=run_id)
            interactions.append(interaction)
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id
        }
