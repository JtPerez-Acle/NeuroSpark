# Synthetic Data Generation Enhancement Plan

## Overview

This document outlines the plan for enhancing the synthetic data generation capabilities of the KQML Parser Backend to support four distinct simulation scenarios:

1. **Prisoners' Dilemma (PD)**
2. **Predator/Prey Dynamics (PP)**
3. **Pursuer/Evader (PE) Dynamics**
4. **Search and Rescue (S&R)**

Each scenario models different agent interaction patterns that can be used to study complex systems such as cooperation dynamics, information propagation, crime dynamics, and knowledge transfer.

## Simulation Scenarios

### 1. Prisoners' Dilemma (PD)
- **Purpose**: Study cooperation and defection effects on environmental resource management
- **Application**: Identify strategies to avoid tragedy of the commons
- **Dynamics**: Self-aware agents negotiate and cooperate to establish collective intelligence for resource management
- **Key Interactions**: Cooperation vs. defection with scoring matrix

### 2. Predator/Prey Dynamics (PP)
- **Purpose**: Analyze dispersion of fake vs. factual news
- **Application**: Devise strategies against misinformation
- **Dynamics**: Information spreading within a network of aware agents with memory
- **Key Interactions**: Information propagation with credibility and susceptibility factors

### 3. Pursuer/Evader (PE) Dynamics
- **Purpose**: Study crime dynamics in complex urban scenarios
- **Application**: Develop strategies to reduce criminality 
- **Dynamics**: Strategies employed by self-aware pursuers and evaders
- **Key Interactions**: Evasion tactics, pursuit efficiency, environmental factors

### 4. Search and Rescue (S&R)
- **Purpose**: Study knowledge transfer between unrelated Agent-Based Simulations
- **Application**: Improve search, identification and rescue operations
- **Dynamics**: Agent navigation in complex environments with obstacles
- **Key Interactions**: Searching, identifying, and rescuing hidden agents

## Implementation Plan

### 1. Modular Architecture

We'll extend the existing DataGenerator class using a modular approach:

```
DataGenerator (Base Class)
├── ScenarioGenerator (Interface)
│   ├── PDScenarioGenerator (Prisoners' Dilemma)
│   ├── PPScenarioGenerator (Predator/Prey)
│   ├── PEScenarioGenerator (Pursuer/Evader)
│   └── SARScenarioGenerator (Search and Rescue)
```

This approach will:
- Keep the core DataGenerator functionality intact
- Allow independent development of each scenario
- Make maintenance easier
- Provide a consistent interface for all scenarios

### 2. Modified Class Structure

```python
class DataGenerator:
    """Generate synthetic data for testing."""
    
    def __init__(self, scenario=None):
        """Initialize with option to specify a scenario."""
        # Original initialization
        # ...
        
        self.scenario = scenario
        self.scenario_generator = self._create_scenario_generator(scenario)
    
    def _create_scenario_generator(self, scenario):
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
    
    # Original methods remain unchanged
    # ...
    
    def generate_scenario_data(self, num_agents, num_interactions, **kwargs):
        """Generate data for the selected scenario."""
        if self.scenario_generator:
            return self.scenario_generator.generate_data(num_agents, num_interactions, **kwargs)
        else:
            # Fall back to standard synthetic data generation
            return self.generate_synthetic_data(num_agents, num_interactions)


class ScenarioGenerator:
    """Base interface for scenario generators."""
    
    def generate_data(self, num_agents, num_interactions, **kwargs):
        """Generate data for the scenario."""
        raise NotImplementedError("Subclasses must implement generate_data")
    
    def create_agent(self, **kwargs):
        """Create an agent for this scenario."""
        raise NotImplementedError("Subclasses must implement create_agent")
    
    def generate_interaction(self, sender, receiver, **kwargs):
        """Generate an interaction between agents."""
        raise NotImplementedError("Subclasses must implement generate_interaction")
```

### 3. Scenario-Specific Implementations

Each scenario will implement the following:

1. **Custom agent types and roles**
   - Define agent properties specific to the scenario
   - Implement specialized behavior patterns

2. **Specialized interaction modeling**
   - Define interaction types and outcomes
   - Implement scenario rules and dynamics
   - Incorporate mathematical models for success/failure

3. **Scenario state management**
   - Track scenario-specific state (rounds, positions, etc.)
   - Update agents based on interaction outcomes

### 4. API Integration

Extend the existing API to support scenario-based generation:

```python
@generate_router.post("/scenario",
    response_model=Dict[str, Any],
    summary="Generate Scenario-Based Data",
    description="Generate synthetic data based on a specific simulation scenario."
)
async def generate_scenario_data(
    request: Request,
    scenario: str = Query(..., description="Scenario type (pd, predator_prey, pursuer_evader, search_rescue)"),
    num_agents: int = Query(10, description="Number of agents to generate"),
    num_interactions: int = Query(50, description="Number of interactions to generate"),
    rounds: Optional[int] = Query(None, description="Number of rounds/time steps (scenario-specific)")
) -> Dict[str, Any]:
    """Generate synthetic data for a specific scenario."""
    try:
        db = get_db(request)
        generator = DataGenerator(scenario)
        
        # Generate scenario-specific data
        kwargs = {}
        if rounds is not None:
            kwargs["rounds"] = rounds
            
        data = generator.generate_scenario_data(num_agents, num_interactions, **kwargs)
        
        # Store agents and interactions
        for agent in data["agents"]:
            await db.store_agent(agent)
        
        for interaction in data["interactions"]:
            await db.store_interaction(interaction)
        
        return {
            "status": "success",
            "scenario": scenario,
            "data": data
        }
    except Exception as e:
        logger.error(f"Error generating scenario data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

## Implementation Details by Scenario

### 1. Prisoners' Dilemma Implementation

```python
class PDScenarioGenerator(ScenarioGenerator):
    """Prisoners' Dilemma scenario generator."""
    
    def __init__(self):
        self.agent_roles = ["cooperator", "defector", "tit_for_tat", "random"]
        self.payoff_matrix = {
            ("cooperate", "cooperate"): (3, 3),  # Both cooperate: mutual benefit
            ("cooperate", "defect"): (0, 5),     # Sender cooperates, receiver defects
            ("defect", "cooperate"): (5, 0),     # Sender defects, receiver cooperates
            ("defect", "defect"): (1, 1)         # Both defect: mutual punishment
        }
    
    def create_agent(self, role=None):
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
    
    def generate_interaction(self, sender, receiver, round_num=1):
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
    
    def _get_decision(self, agent, opponent):
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
    
    def generate_data(self, num_agents, num_interactions, rounds=10):
        """Generate PD scenario data."""
        # Create agents
        agents = [self.create_agent() for _ in range(num_agents)]
        
        # Create a run ID
        run_id = str(uuid.uuid4()).replace('-', '_')
        
        # Generate interactions through rounds of play
        interactions = []
        for round_num in range(1, rounds + 1):
            # Each agent plays against every other agent once per round
            for i in range(num_agents):
                for j in range(i + 1, num_agents):
                    sender = agents[i]
                    receiver = agents[j]
                    
                    interaction = self.generate_interaction(sender, receiver, round_num)
                    interaction["run_id"] = run_id
                    interactions.append(interaction)
                    
                    # In a real implementation, we would update agent histories here
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id,
            "scenario": "prisoners_dilemma"
        }
```

### 2. Predator/Prey Implementation

The Predator/Prey scenario will focus on information diffusion dynamics, modeling factual vs. fake news propagation:

```python
class PPScenarioGenerator(ScenarioGenerator):
    """Predator/Prey scenario generator."""
    
    def __init__(self):
        self.agent_types = ["predator", "prey"]
        self.predator_roles = ["misinformation", "disinformation", "propaganda"]
        self.prey_roles = ["factchecker", "skeptic", "vulnerable"]
        self.interaction_types = ["share", "consume", "verify", "debunk", "amplify"]
    
    def create_agent(self, agent_type=None, role=None):
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
            "credibility": random.uniform(0.1, 0.9),
            "influence": random.uniform(0.2, 0.8),
            "network": [],
            "information": []
        }
        
        # Type-specific properties
        if agent_type == "predator":
            agent["virality_factor"] = random.uniform(0.5, 1.0)
            agent["concealment"] = random.uniform(0.3, 0.9)
        else:  # prey
            agent["verification_ability"] = random.uniform(0.2, 0.9)
            agent["susceptibility"] = random.uniform(0.1, 0.8)
        
        return agent
    
    def generate_interaction(self, sender, receiver):
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
            credibility = sender["credibility"] * (1 - receiver["verification_ability"])
            topic = random.choice(["politics", "health", "science", "celebrity", "finance"])
            
            message = f"{sender['role']} {info_id} shared with {receiver['role']} on {topic} topic"
            success = random.random() < (sender["influence"] * receiver["susceptibility"])
            
        else:  # prey as sender
            if sender["role"] == "factchecker":
                interaction_type = "debunk"
                credibility = sender["credibility"] * (1 + sender["verification_ability"])
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
    
    def generate_data(self, num_agents, num_interactions, **kwargs):
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
```

### 3. Pursuer/Evader Implementation

The Pursuer/Evader scenario will model crime dynamics in urban environments:

```python
class PEScenarioGenerator(ScenarioGenerator):
    """Pursuer/Evader scenario generator."""
    
    def __init__(self):
        self.agent_types = ["pursuer", "evader"]
        self.pursuer_roles = ["patrol", "detective", "response"]
        self.evader_roles = ["burglar", "vandal", "organized"]
        self.interaction_types = ["chase", "evade", "hide", "search", "capture", "escape"]
    
    def create_agent(self, agent_type=None, role=None):
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
    
    def generate_interaction(self, sender, receiver, time_step=0):
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
    
    def generate_data(self, num_agents, num_interactions, time_steps=20):
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
        
        return {
            "agents": agents,
            "interactions": interactions,
            "run_id": run_id,
            "scenario": "pursuer_evader"
        }
```

### 4. Search and Rescue Implementation

The Search and Rescue scenario will model knowledge transfer between agents in complex environments:

```python
class SARScenarioGenerator(ScenarioGenerator):
    """Search and Rescue scenario generator."""
    
    def __init__(self):
        self.agent_types = ["searcher", "coordinator", "victim"]
        self.searcher_roles = ["aerial", "ground", "technical"]
        self.coordinator_roles = ["command", "logistics", "communications"]
        self.victim_roles = ["injured", "trapped", "lost"]
        self.interaction_types = ["search", "locate", "coordinate", "extract", "communicate"]
    
    def create_agent(self, agent_type=None, role=None):
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
    
    def generate_interaction(self, sender, receiver):
        """Generate a Search and Rescue interaction."""
        # Calculate distance between agents
        distance = ((sender["position"]["x"] - receiver["position"]["x"])**2 + 
                   (sender["position"]["y"] - receiver["position"]["y"])**2)**0.5
        
        # Determine interaction type based on agent types
        if sender["type"] == "searcher" and receiver["type"] == "victim":
            # Check if victim is within search radius
            if distance <= sender["search_radius"]:
                detection_probability = sender["knowledge_level"] * receiver["visibility"]
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
                success_probability = sender["visibility"] * (1 - sender["mobility"])
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
                "environment_complexity": random.uniform(0.3, 0.9)
            }
        }
        
        return interaction
    
    def generate_data(self, num_agents, num_interactions, **kwargs):
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
```

## Next Steps

1. **Implementation Phases**:
   - Phase 1: Define the interfaces and base classes
   - Phase 2: Implement the Prisoners' Dilemma scenario
   - Phase 3: Add the remaining scenarios
   - Phase 4: Integrate with the API

2. **Testing**:
   - Unit tests for each scenario generator
   - Integration tests for the API endpoints
   - Validation of generated data against scenario requirements

3. **Documentation**:
   - Update API documentation
   - Add usage examples for each scenario
   - Document the data structures for each scenario

4. **Future Enhancements**:
   - Parameter tuning for more realistic simulations
   - Visualization tools for scenario outcomes
   - Advanced analysis of interaction patterns
   - Addition of more complex scenarios