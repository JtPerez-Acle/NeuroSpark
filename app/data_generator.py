"""Data generator module for creating synthetic agent interactions."""
from datetime import datetime, timezone
import random
import uuid
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod

from app.kqml_handler import generate_synthetic_interaction

class ScenarioGenerator(ABC):
    """Base interface for scenario generators."""
    
    @abstractmethod
    def generate_data(self, num_agents: int, num_interactions: int, **kwargs) -> Dict[str, Any]:
        """Generate data for the scenario."""
        pass
    
    @abstractmethod
    def create_agent(self, **kwargs) -> Dict[str, Any]:
        """Create an agent for this scenario."""
        pass
    
    @abstractmethod
    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate an interaction between agents."""
        pass


class PDScenarioGenerator(ScenarioGenerator):
    """Prisoners' Dilemma scenario generator."""
    
    def __init__(self):
        """Initialize PDScenarioGenerator."""
        self.agent_roles = ["cooperator", "defector", "tit_for_tat", "random"]
        self.payoff_matrix = {
            ("cooperate", "cooperate"): (3, 3),  # Both cooperate: mutual benefit
            ("cooperate", "defect"): (0, 5),     # Sender cooperates, receiver defects
            ("defect", "cooperate"): (5, 0),     # Sender defects, receiver cooperates
            ("defect", "defect"): (1, 1)         # Both defect: mutual punishment
        }
    
    def create_agent(self, role: Optional[str] = None) -> Dict[str, Any]:
        """Create a PD agent."""
        role = role or random.choice(self.agent_roles)
        
        agent = {
            "id": str(uuid.uuid4()).replace('-', '_'),
            "type": "prisoner",
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "score": 0,
            "history": [],
            "strategy": role
        }
        
        return agent
    
    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any], 
                            round_num: int = 1) -> Dict[str, Any]:
        """Generate a PD interaction."""
        # Determine decisions based on strategies
        sender_decision = self._get_decision(sender, receiver)
        receiver_decision = self._get_decision(receiver, sender)
        
        # Calculate payoffs
        sender_payoff, receiver_payoff = self.payoff_matrix[(sender_decision, receiver_decision)]
        
        message = f"Round {round_num}: {sender['role']} {sender_decision}s, {receiver['role']} {receiver_decision}s. Payoffs: {sender_payoff}, {receiver_payoff}"
        
        # Create interaction data
        interaction = {
            "interaction_id": str(uuid.uuid4()).replace('-', '_'),
            "timestamp": datetime.now().isoformat(),
            "sender_id": sender["id"],
            "receiver_id": receiver["id"],
            "topic": "round_decision",
            "message": message,
            "interaction_type": sender_decision,
            "metadata": {
                "scenario": "prisoners_dilemma",
                "round": round_num,
                "sender_decision": sender_decision,
                "receiver_decision": receiver_decision,
                "sender_payoff": sender_payoff,
                "receiver_payoff": receiver_payoff
            }
        }
        
        return interaction
    
    def _get_decision(self, agent: Dict[str, Any], opponent: Dict[str, Any]) -> str:
        """Determine an agent's decision based on strategy."""
        strategy = agent["strategy"]
        
        if strategy == "cooperator":
            return "cooperate"
        elif strategy == "defector":
            return "defect"
        elif strategy == "tit_for_tat":
            # First round: cooperate
            if not agent["history"]:
                return "cooperate"
            # Otherwise: copy opponent's last move
            return agent["history"][-1]
        else:  # random
            return random.choice(["cooperate", "defect"])
    
    def generate_data(self, num_agents: int, num_interactions: int, rounds: int = 10, **kwargs) -> Dict[str, Any]:
        """Generate PD scenario data."""
        # Create agents
        agents = [self.create_agent() for _ in range(num_agents)]
        
        # Create a run ID
        run_id = str(uuid.uuid4()).replace('-', '_')
        
        # Generate interactions through rounds of play
        interactions = []
        for round_num in range(1, rounds + 1):
            # Each agent plays against other agents
            for i in range(num_agents):
                for j in range(i + 1, num_agents):
                    sender = agents[i]
                    receiver = agents[j]
                    
                    interaction = self.generate_interaction(sender, receiver, round_num)
                    interaction["run_id"] = run_id
                    interactions.append(interaction)
                    
                    # In a real implementation, we would update agent histories here
                    
            # Limit to requested number of interactions if specified
            if len(interactions) >= num_interactions:
                interactions = interactions[:num_interactions]
                break
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id,
            "scenario": "prisoners_dilemma"
        }


class PPScenarioGenerator(ScenarioGenerator):
    """Predator/Prey scenario generator."""
    
    def __init__(self):
        """Initialize PPScenarioGenerator."""
        self.agent_types = ["predator", "prey"]
        self.predator_roles = ["misinformation", "disinformation", "propaganda"]
        self.prey_roles = ["factchecker", "skeptic", "vulnerable"]
        self.interaction_types = ["share", "consume", "verify", "debunk", "amplify"]
    
    def create_agent(self, agent_type: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """Create a Predator/Prey agent."""
        if not agent_type:
            agent_type = random.choice(self.agent_types)
            
        if not role:
            if agent_type == "predator":
                role = random.choice(self.predator_roles)
            else:
                role = random.choice(self.prey_roles)
        
        # Common properties
        agent = {
            "id": str(uuid.uuid4()).replace('-', '_'),
            "type": agent_type,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "credibility": round(random.uniform(0.1, 0.9), 2),
            "influence": round(random.uniform(0.2, 0.8), 2),
            "network": [],
            "information": []
        }
        
        # Type-specific properties
        if agent_type == "predator":
            agent["virality_factor"] = round(random.uniform(0.5, 1.0), 2)
            agent["concealment"] = round(random.uniform(0.3, 0.9), 2)
        else:  # prey
            agent["verification_ability"] = round(random.uniform(0.2, 0.9), 2)
            agent["susceptibility"] = round(random.uniform(0.1, 0.8), 2)
        
        return agent
    
    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a Predator/Prey interaction."""
        # Determine interaction type based on agent types
        if sender["type"] == "predator":
            if random.random() < sender["virality_factor"]:
                interaction_type = "share"
            else:
                interaction_type = "amplify"
            
            # Generate misinformation content
            info_id = str(uuid.uuid4())[:8]
            info_type = sender["role"]
            credibility = sender["credibility"] * (1 - receiver.get("verification_ability", 0.5))
            topic = random.choice(["politics", "health", "science", "celebrity", "finance"])
            
            message = f"{sender['role']} {info_id} shared with {receiver['role']} on {topic} topic"
            success = random.random() < (sender["influence"] * receiver.get("susceptibility", 0.5))
            
        else:  # prey as sender
            if sender["role"] == "factchecker":
                interaction_type = "debunk"
                credibility = sender["credibility"] * (1 + sender.get("verification_ability", 0.5))
            elif sender["role"] == "skeptic":
                interaction_type = "verify"
                credibility = sender["credibility"]
            else:
                interaction_type = "consume"
                credibility = sender["credibility"] * 0.8
                
            info_id = str(uuid.uuid4())[:8]
            info_type = "factual"
            topic = random.choice(["politics", "health", "science", "celebrity", "finance"])
            
            message = f"{sender['role']} {interaction_type}s information with {receiver['role']} on {topic} topic"
            success = random.random() < sender["influence"]
        
        # Create interaction data
        interaction = {
            "interaction_id": str(uuid.uuid4()).replace('-', '_'),
            "timestamp": datetime.now().isoformat(),
            "sender_id": sender["id"],
            "receiver_id": receiver["id"],
            "topic": topic,
            "message": message,
            "interaction_type": interaction_type,
            "metadata": {
                "scenario": "predator_prey",
                "info_id": info_id,
                "info_type": info_type,
                "credibility": round(credibility, 2),
                "success": success,
                "topic": topic
            }
        }
        
        return interaction
    
    def generate_data(self, num_agents: int, num_interactions: int, **kwargs) -> Dict[str, Any]:
        """Generate Predator/Prey scenario data."""
        # Determine number of each type
        num_predators = max(1, num_agents // 3)
        num_prey = num_agents - num_predators
        
        # Create agents
        predators = [self.create_agent("predator") for _ in range(num_predators)]
        prey = [self.create_agent("prey") for _ in range(num_prey)]
        agents = predators + prey
        
        # Create a run ID
        run_id = str(uuid.uuid4()).replace('-', '_')
        
        # Generate interactions
        interactions = []
        for _ in range(num_interactions):
            # Select agents based on interaction probability
            if random.random() < 0.7:  # 70% chance of predator->prey interaction
                sender = random.choice(predators)
                receiver = random.choice(prey)
            elif random.random() < 0.2:  # 20% chance of prey->prey
                sender = random.choice(prey)
                receiver = random.choice(prey)
                while sender["id"] == receiver["id"]:
                    receiver = random.choice(prey)
            else:  # 10% chance of prey->predator
                sender = random.choice(prey)
                receiver = random.choice(predators)
            
            interaction = self.generate_interaction(sender, receiver)
            interaction["run_id"] = run_id
            interactions.append(interaction)
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id,
            "scenario": "predator_prey"
        }


class PEScenarioGenerator(ScenarioGenerator):
    """Pursuer/Evader scenario generator."""
    
    def __init__(self):
        """Initialize PEScenarioGenerator."""
        self.agent_types = ["pursuer", "evader"]
        self.pursuer_roles = ["patrol", "detective", "response"]
        self.evader_roles = ["burglar", "vandal", "organized"]
        self.interaction_types = ["chase", "evade", "hide", "search", "capture", "escape"]
    
    def create_agent(self, agent_type: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """Create a Pursuer/Evader agent."""
        if not agent_type:
            agent_type = random.choice(self.agent_types)
            
        if not role:
            if agent_type == "pursuer":
                role = random.choice(self.pursuer_roles)
            else:
                role = random.choice(self.evader_roles)
        
        # Common properties
        agent = {
            "id": str(uuid.uuid4()).replace('-', '_'),
            "type": agent_type,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "position": {
                "x": round(random.uniform(0, 100), 2),
                "y": round(random.uniform(0, 100), 2)
            },
            "speed": round(random.uniform(1, 5), 2),
            "knowledge": round(random.uniform(0.2, 0.9), 2)
        }
        
        # Type-specific properties
        if agent_type == "pursuer":
            agent["detection_radius"] = round(random.uniform(5, 15), 2)
            agent["authority_level"] = random.randint(1, 5)
        else:  # evader
            agent["stealth"] = round(random.uniform(0.3, 0.9), 2)
            agent["crime_type"] = random.choice(["theft", "vandalism", "fraud", "trespass"])
        
        return agent
    
    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any], 
                           time_step: int = 0) -> Dict[str, Any]:
        """Generate a Pursuer/Evader interaction."""
        # Calculate distance between agents
        distance = ((sender["position"]["x"] - receiver["position"]["x"])**2 + 
                   (sender["position"]["y"] - receiver["position"]["y"])**2)**0.5
        
        # Determine interaction type based on agent types and distance
        if sender["type"] == "pursuer" and receiver["type"] == "evader":
            detection_probability = sender["knowledge"] * (1 - receiver["stealth"]) * (1 / max(1, distance/10))
            detected = random.random() < detection_probability
            
            if detected:
                if distance < sender["detection_radius"]:
                    interaction_type = "capture"
                    message = f"{sender['role']} captured {receiver['role']} at coordinates ({receiver['position']['x']:.1f}, {receiver['position']['y']:.1f})"
                    success = True
                else:
                    interaction_type = "chase"
                    message = f"{sender['role']} pursuing {receiver['role']} at distance {distance:.1f}"
                    success = False
            else:
                interaction_type = "search"
                message = f"{sender['role']} searching for suspects near ({sender['position']['x']:.1f}, {sender['position']['y']:.1f})"
                success = False
                
        elif sender["type"] == "evader" and receiver["type"] == "pursuer":
            evasion_probability = sender["stealth"] * (1 - receiver["knowledge"]) * (distance/20)
            successful_evasion = random.random() < evasion_probability
            
            if successful_evasion:
                interaction_type = "hide"
                message = f"{sender['role']} successfully hiding from {receiver['role']}"
                success = True
            else:
                interaction_type = "evade"
                message = f"{sender['role']} attempting to evade {receiver['role']}"
                success = False
        
        else:  # Same type interactions
            interaction_type = "communicate"
            message = f"{sender['type']} {sender['id']} communicating with {receiver['type']} {receiver['id']}"
            success = True
        
        # Create interaction data
        interaction = {
            "interaction_id": str(uuid.uuid4()).replace('-', '_'),
            "timestamp": datetime.now().isoformat(),
            "sender_id": sender["id"],
            "receiver_id": receiver["id"],
            "topic": "crime_dynamics",
            "message": message,
            "interaction_type": interaction_type,
            "metadata": {
                "scenario": "pursuer_evader",
                "time_step": time_step,
                "distance": round(distance, 2),
                "success": success,
                "sender_position": sender["position"],
                "receiver_position": receiver["position"],
                "environment": "urban"
            }
        }
        
        return interaction
    
    def generate_data(self, num_agents: int, num_interactions: int, time_steps: int = 20, **kwargs) -> Dict[str, Any]:
        """Generate Pursuer/Evader scenario data."""
        # Determine number of each type
        num_pursuers = max(1, num_agents // 3)
        num_evaders = num_agents - num_pursuers
        
        # Create agents
        pursuers = [self.create_agent("pursuer") for _ in range(num_pursuers)]
        evaders = [self.create_agent("evader") for _ in range(num_evaders)]
        agents = pursuers + evaders
        
        # Create a run ID
        run_id = str(uuid.uuid4()).replace('-', '_')
        
        # Generate interactions over time steps
        interactions = []
        for t in range(time_steps):
            # Update positions based on simple movement model
            for agent in agents:
                agent["position"]["x"] += random.uniform(-5, 5) * agent["speed"] / 5
                agent["position"]["y"] += random.uniform(-5, 5) * agent["speed"] / 5
                
                # Keep within bounds
                agent["position"]["x"] = max(0, min(100, agent["position"]["x"]))
                agent["position"]["y"] = max(0, min(100, agent["position"]["y"]))
            
            # Generate interactions for this time step
            interactions_per_step = max(1, num_interactions // time_steps)
            for _ in range(interactions_per_step):
                # Select interacting agents
                if random.random() < 0.7:  # 70% pursuer->evader interactions
                    sender = random.choice(pursuers)
                    receiver = random.choice(evaders)
                else:  # 30% evader->pursuer interactions
                    sender = random.choice(evaders)
                    receiver = random.choice(pursuers)
                    
                interaction = self.generate_interaction(sender, receiver, t)
                interaction["run_id"] = run_id
                interactions.append(interaction)
                
                # Limit to requested number of interactions if specified
                if len(interactions) >= num_interactions:
                    break
                    
            if len(interactions) >= num_interactions:
                break
        
        return {
            "agents": agents,
            "interactions": interactions[:num_interactions],
            "run_id": run_id,
            "scenario": "pursuer_evader"
        }


class SARScenarioGenerator(ScenarioGenerator):
    """Search and Rescue scenario generator."""
    
    def __init__(self):
        """Initialize SARScenarioGenerator."""
        self.agent_types = ["searcher", "coordinator", "victim"]
        self.searcher_roles = ["aerial", "ground", "technical"]
        self.coordinator_roles = ["command", "logistics", "communications"]
        self.victim_roles = ["injured", "trapped", "lost"]
        self.interaction_types = ["search", "locate", "coordinate", "extract", "communicate"]
    
    def create_agent(self, agent_type: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """Create a Search and Rescue agent."""
        if not agent_type:
            agent_type = random.choice(self.agent_types)
            
        if not role:
            if agent_type == "searcher":
                role = random.choice(self.searcher_roles)
            elif agent_type == "coordinator":
                role = random.choice(self.coordinator_roles)
            else:
                role = random.choice(self.victim_roles)
        
        # Common properties
        agent = {
            "id": str(uuid.uuid4()).replace('-', '_'),
            "type": agent_type,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "position": {
                "x": round(random.uniform(0, 100), 2),
                "y": round(random.uniform(0, 100), 2)
            },
            "knowledge_level": round(random.uniform(0.2, 0.9), 2)
        }
        
        # Type-specific properties
        if agent_type == "searcher":
            agent["search_radius"] = round(random.uniform(5, 20), 2)
            agent["battery"] = 100
            agent["equipment"] = random.choice(["thermal", "radar", "camera", "audio"])
        elif agent_type == "coordinator":
            agent["coordination_radius"] = round(random.uniform(30, 100), 2)
            agent["resources"] = random.randint(3, 10)
            agent["position"] = {"x": 50, "y": 50}  # Central position
        else:  # victim
            agent["visibility"] = round(random.uniform(0.1, 0.7), 2)
            agent["mobility"] = round(random.uniform(0, 0.5), 2)
            agent["status"] = random.choice(["critical", "stable", "unknown"])
            agent["found"] = False
            agent["rescued"] = False
        
        return agent
    
    def generate_interaction(self, sender: Dict[str, Any], receiver: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a Search and Rescue interaction."""
        # Calculate distance between agents
        distance = ((sender["position"]["x"] - receiver["position"]["x"])**2 + 
                   (sender["position"]["y"] - receiver["position"]["y"])**2)**0.5
        
        # Determine interaction type based on agent types
        if sender["type"] == "searcher" and receiver["type"] == "victim":
            # Check if victim is within search radius
            if distance <= sender.get("search_radius", 10):
                detection_probability = sender["knowledge_level"] * receiver.get("visibility", 0.5)
                detected = random.random() < detection_probability
                
                if detected:
                    interaction_type = "locate"
                    message = f"{sender['role']} located {receiver['role']} victim at ({receiver['position']['x']:.1f}, {receiver['position']['y']:.1f})"
                    # In actual implementation: receiver["found"] = True
                else:
                    interaction_type = "search"
                    message = f"{sender['role']} searching near {receiver['role']} victim but unable to locate"
            else:
                interaction_type = "search"
                message = f"{sender['role']} searching area at ({sender['position']['x']:.1f}, {sender['position']['y']:.1f})"
                
        elif sender["type"] == "coordinator":
            if receiver["type"] == "searcher":
                interaction_type = "coordinate"
                message = f"{sender['role']} coordinating {receiver['role']} search pattern"
            elif receiver["type"] == "victim" and receiver.get("found", False):
                interaction_type = "plan_rescue"
                message = f"{sender['role']} planning rescue for {receiver['role']} victim"
            else:
                interaction_type = "communicate"
                message = f"{sender['role']} communicating with other team members"
        
        elif sender["type"] == "victim":
            if receiver["type"] == "searcher" and distance <= 15:
                interaction_type = "signal"
                success_probability = sender.get("visibility", 0.5) * (1 - sender.get("mobility", 0.5))
                success = random.random() < success_probability
                message = f"{sender['role']} victim signaling to nearby {receiver['role']}"
            else:
                interaction_type = "wait"
                message = f"{sender['role']} victim waiting for rescue"
        
        else:  # Searcher to Searcher or other combinations
            interaction_type = "communicate"
            message = f"{sender['type']} {sender['id']} communicating with {receiver['type']} {receiver['id']}"
        
        # Create interaction data
        interaction = {
            "interaction_id": str(uuid.uuid4()).replace('-', '_'),
            "timestamp": datetime.now().isoformat(),
            "sender_id": sender["id"],
            "receiver_id": receiver["id"],
            "topic": "rescue_operation",
            "message": message,
            "interaction_type": interaction_type,
            "metadata": {
                "scenario": "search_rescue",
                "distance": round(distance, 2),
                "sender_position": sender["position"],
                "receiver_position": receiver["position"],
                "environment_complexity": round(random.uniform(0.3, 0.9), 2)
            }
        }
        
        return interaction
    
    def generate_data(self, num_agents: int, num_interactions: int, **kwargs) -> Dict[str, Any]:
        """Generate Search and Rescue scenario data."""
        # Determine number of each type
        num_victims = max(1, num_agents // 5)
        num_coordinators = max(1, num_agents // 10)
        num_searchers = num_agents - num_victims - num_coordinators
        
        # Create agents
        searchers = [self.create_agent("searcher") for _ in range(num_searchers)]
        coordinators = [self.create_agent("coordinator") for _ in range(num_coordinators)]
        victims = [self.create_agent("victim") for _ in range(num_victims)]
        agents = searchers + coordinators + victims
        
        # Create a run ID
        run_id = str(uuid.uuid4()).replace('-', '_')
        
        # Generate interactions
        interactions = []
        for _ in range(num_interactions):
            # Select interacting agents based on probabilities
            rand = random.random()
            
            if rand < 0.6:  # 60% searcher->victim
                sender = random.choice(searchers)
                receiver = random.choice(victims)
            elif rand < 0.8:  # 20% coordinator->searcher
                sender = random.choice(coordinators)
                receiver = random.choice(searchers)
            elif rand < 0.9:  # 10% victim->searcher
                sender = random.choice(victims)
                receiver = random.choice(searchers)
            else:  # 10% searcher->searcher
                sender = random.choice(searchers)
                receiver = random.choice(searchers)
                while sender["id"] == receiver["id"]:
                    receiver = random.choice(searchers)
                    
            interaction = self.generate_interaction(sender, receiver)
            interaction["run_id"] = run_id
            interactions.append(interaction)
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id,
            "scenario": "search_rescue"
        }


class DataGenerator:
    """Generate synthetic data for testing."""
    
    def __init__(self, scenario: Optional[str] = None):
        """Initialize data generator with agent types and roles."""
        # Original agent types and roles
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
        
        # Set up scenario generator if provided
        self.scenario = scenario
        self.scenario_generator = self._create_scenario_generator(scenario)
    
    def _create_scenario_generator(self, scenario: Optional[str]) -> Optional[ScenarioGenerator]:
        """Create appropriate scenario generator."""
        if scenario == "pd":
            return PDScenarioGenerator()
        elif scenario == "predator_prey":
            return PPScenarioGenerator()
        elif scenario == "pursuer_evader":
            return PEScenarioGenerator()
        elif scenario == "search_rescue":
            return SARScenarioGenerator()
        return None  # Default to standard generation
        
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
        
    def generate_scenario_data(self, num_agents: int, num_interactions: int, **kwargs) -> Dict[str, Any]:
        """Generate data for the selected scenario."""
        if self.scenario_generator:
            return self.scenario_generator.generate_data(num_agents, num_interactions, **kwargs)
        else:
            # Fall back to standard synthetic data generation
            return self.generate_synthetic_data(num_agents, num_interactions)
