"""In-memory database implementation for testing."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from .base import DatabaseInterface

class InMemoryDatabase(DatabaseInterface):
    """In-memory database implementation for testing."""
    
    def __init__(self):
        """Initialize in-memory database."""
        self.agents = {}
        self.runs = {}
        self.interactions = []
    
    async def connect(self) -> None:
        """No-op for in-memory database."""
        pass
    
    async def disconnect(self) -> None:
        """No-op for in-memory database."""
        pass
    
    async def store_message(self, message_data: Dict[str, Any]) -> None:
        """Store a message in memory."""
        self.agents.setdefault(message_data["sender"], {"id": message_data["sender"], "interactions": [], "runs": set()})
        self.agents.setdefault(message_data["receiver"], {"id": message_data["receiver"], "interactions": [], "runs": set()})
        self.interactions.append(message_data)
    
    async def store_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """Store an interaction in the database."""
        # Ensure required fields are present
        required_fields = ["sender", "receiver", "performative", "content", "timestamp"]
        if not all(field in interaction_data for field in required_fields):
            raise ValueError(f"Missing required fields in interaction data. Required: {required_fields}")

        # Generate or use existing message_id
        if "message_id" not in interaction_data:
            interaction_data["message_id"] = interaction_data.get("id", str(uuid.uuid4()))
        
        # Ensure id is consistent with message_id
        interaction_data["id"] = interaction_data["message_id"]
        
        # Store the interaction
        self.interactions.append(interaction_data)

        # Create or update agents
        agent_ids = [interaction_data["sender"], interaction_data["receiver"]]
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                self.agents[agent_id] = {
                    "id": agent_id,
                    "interactions": [],
                    "runs": set()
                }
            self.agents[agent_id]["interactions"].append(interaction_data["message_id"])

        # Update run if present
        if "run_id" in interaction_data:
            run_id = interaction_data["run_id"]
            if run_id not in self.runs:
                self.runs[run_id] = {
                    "id": run_id,
                    "interactions": [],
                    "agents": set(),
                    "timestamp": interaction_data["timestamp"]
                }
            self.runs[run_id]["interactions"].append(interaction_data["message_id"])
            self.runs[run_id]["agents"].update(agent_ids)
            
            # Update agents with run information
            for agent_id in agent_ids:
                self.agents[agent_id]["runs"].add(run_id)

    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes from memory."""
        nodes = []
        
        # Add agent nodes
        for agent_id, agent_data in self.agents.items():
            nodes.append({
                "id": agent_id,
                "label": "Agent",
                "properties": {"agent_id": agent_id}
            })
        
        # Add run nodes
        for run_id, run_data in self.runs.items():
            nodes.append({
                "id": run_id,
                "label": "Run",
                "properties": {
                    "run_id": run_id,
                    "timestamp": run_data["timestamp"]
                }
            })
        
        # Add interaction nodes
        for interaction in self.interactions:
            nodes.append({
                "id": interaction["id"],
                "label": "Interaction",
                "properties": {
                    "sender": interaction["sender"],
                    "receiver": interaction["receiver"],
                    "content": interaction["content"],
                    "performative": interaction["performative"],
                    "timestamp": interaction["timestamp"]
                }
            })
        
        return nodes
    
    async def get_all_relationships(self) -> List[Dict[str, Any]]:
        """Get all relationships from memory."""
        relationships = []
        
        for interaction in self.interactions:
            # Add SENT relationship
            relationships.append({
                "source": interaction["sender"],
                "target": interaction["id"],
                "type": "SENT"
            })
            
            # Add RECEIVED_BY relationship
            relationships.append({
                "source": interaction["id"],
                "target": interaction["receiver"],
                "type": "RECEIVED_BY"
            })
            
            # Add PART_OF relationship if run_id exists
            if "run_id" in interaction:
                relationships.append({
                    "source": interaction["id"],
                    "target": interaction["run_id"],
                    "type": "PART_OF"
                })
        
        return relationships
    
    async def query_nodes(self, query: Any) -> List[Dict[str, Any]]:
        """Query nodes with filters from memory."""
        nodes = await self.get_all_nodes()
        filtered_nodes = []
        
        for node in nodes:
            # Apply node type filter
            if hasattr(query, 'nodeTypes') and query.nodeTypes:
                if node["label"] not in query.nodeTypes:
                    continue
            
            # Apply time range filter
            if (hasattr(query, 'timeRange') and query.timeRange and 
                query.timeRange.get("start") and "timestamp" in node["properties"]):
                timestamp = node["properties"]["timestamp"]
                if timestamp < query.timeRange["start"]:
                    continue
                if query.timeRange.get("end") and timestamp > query.timeRange["end"]:
                    continue
            
            # Apply agent filter
            if hasattr(query, 'agents') and query.agents:
                if (node["label"] == "Agent" and node["id"] not in query.agents) or \
                   (node["label"] == "Interaction" and 
                    node["properties"]["sender"] not in query.agents and 
                    node["properties"]["receiver"] not in query.agents):
                    continue
            
            # Apply run filter
            if hasattr(query, 'runs') and query.runs:
                if node["label"] == "Run" and node["id"] not in query.runs:
                    continue
            
            filtered_nodes.append(node)
        
        return filtered_nodes
    
    async def query_relationships(self, query: Any) -> List[Dict[str, Any]]:
        """Query relationships with filters from memory."""
        relationships = await self.get_all_relationships()
        filtered_relationships = []
        
        for rel in relationships:
            # Apply relationship type filter
            if hasattr(query, 'relationshipTypes') and query.relationshipTypes:
                if rel["type"] not in query.relationshipTypes:
                    continue
            
            # Apply time range filter
            if hasattr(query, 'timeRange') and query.timeRange and query.timeRange.get("start"):
                # Find the interaction node to get its timestamp
                interaction = next(
                    (i for i in self.interactions if i["id"] == rel["source"] or i["id"] == rel["target"]),
                    None
                )
                if interaction:
                    timestamp = interaction["timestamp"]
                    if timestamp < query.timeRange["start"]:
                        continue
                    if query.timeRange.get("end") and timestamp > query.timeRange["end"]:
                        continue
            
            # Apply agent filter
            if hasattr(query, 'agents') and query.agents:
                if not any(aid in query.agents for aid in [rel["source"], rel["target"]]):
                    continue
            
            # Apply run filter
            if hasattr(query, 'runs') and query.runs:
                if not any(rid in query.runs for rid in [rel["source"], rel["target"]]):
                    continue
            
            filtered_relationships.append(rel)
        
        return filtered_relationships
    
    async def get_agent_runs(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all runs associated with an agent."""
        if agent_id not in self.agents:
            return []
        
        agent_runs = []
        for run_id in self.agents[agent_id]["runs"]:
            if run_id in self.runs:
                agent_runs.append(self.runs[run_id])
        return agent_runs

    async def get_agent_interactions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all interactions associated with an agent."""
        if agent_id not in self.agents:
            return []
        
        agent_interactions = []
        for interaction_id in self.agents[agent_id]["interactions"]:
            interaction = next((i for i in self.interactions if i["message_id"] == interaction_id), None)
            if interaction:
                agent_interactions.append(interaction)
        return agent_interactions
    
    async def get_graph_data(self, node_type: Optional[str] = None, threshold: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get graph data with optional filters."""
        nodes = await self.get_all_nodes()
        relationships = await self.get_all_relationships()
        
        if node_type:
            filtered_nodes = [n for n in nodes if n["label"] == node_type]
            node_ids = {n["id"] for n in filtered_nodes}
            filtered_relationships = [r for r in relationships if r["source"] in node_ids or r["target"] in node_ids]
            nodes = filtered_nodes
            relationships = filtered_relationships
        
        if threshold:
            filtered_nodes = []
            for node in nodes:
                if "timestamp" in node["properties"]:
                    node_time = datetime.fromisoformat(node["properties"]["timestamp"].replace("Z", "+00:00"))
                    if node_time >= threshold:
                        filtered_nodes.append(node)
                else:
                    filtered_nodes.append(node)
            
            node_ids = {n["id"] for n in filtered_nodes}
            filtered_relationships = [r for r in relationships if r["source"] in node_ids and r["target"] in node_ids]
            nodes = filtered_nodes
            relationships = filtered_relationships
        
        return {
            "nodes": nodes,
            "relationships": relationships
        }
    
    async def query_graph(self, query: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Query graph data with filters."""
        nodes = await self.get_all_nodes()
        relationships = await self.get_all_relationships()
        
        # Filter by node type
        if query.get("node_type"):
            filtered_nodes = [n for n in nodes if n["label"] == query["node_type"]]
            node_ids = {n["id"] for n in filtered_nodes}
            filtered_relationships = [r for r in relationships if r["source"] in node_ids or r["target"] in node_ids]
            nodes = filtered_nodes
            relationships = filtered_relationships
        
        # Filter by relationship type
        if query.get("relationship_type"):
            filtered_relationships = [r for r in relationships if r["type"] == query["relationship_type"]]
            node_ids = {r["source"] for r in filtered_relationships} | {r["target"] for r in filtered_relationships}
            filtered_nodes = [n for n in nodes if n["id"] in node_ids]
            nodes = filtered_nodes
            relationships = filtered_relationships
        
        # Filter by time range
        if query.get("start_time") and query.get("end_time"):
            start_time = datetime.fromisoformat(query["start_time"].replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(query["end_time"].replace("Z", "+00:00"))
            
            filtered_nodes = []
            for node in nodes:
                if "timestamp" in node["properties"]:
                    node_time = datetime.fromisoformat(node["properties"]["timestamp"].replace("Z", "+00:00"))
                    if start_time <= node_time <= end_time:
                        filtered_nodes.append(node)
                else:
                    filtered_nodes.append(node)
            
            node_ids = {n["id"] for n in filtered_nodes}
            filtered_relationships = [r for r in relationships if r["source"] in node_ids and r["target"] in node_ids]
            nodes = filtered_nodes
            relationships = filtered_relationships
        
        # Filter by agent IDs
        if query.get("agent_ids"):
            agent_ids = set(query["agent_ids"])
            filtered_nodes = [n for n in nodes if n["id"] in agent_ids or 
                            (n["label"] == "Agent" and n["properties"]["agent_id"] in agent_ids)]
            node_ids = {n["id"] for n in filtered_nodes}
            filtered_relationships = [r for r in relationships if r["source"] in node_ids or r["target"] in node_ids]
            nodes = filtered_nodes
            relationships = filtered_relationships
        
        # Apply limit
        if query.get("limit"):
            nodes = nodes[:query["limit"]]
            node_ids = {n["id"] for n in nodes}
            relationships = [r for r in relationships if r["source"] in node_ids and r["target"] in node_ids]
        
        return {
            "nodes": nodes,
            "relationships": relationships
        }
    
    async def clear_database(self) -> Dict[str, Any]:
        """Clear all data from memory."""
        self.agents.clear()
        self.runs.clear()
        self.interactions.clear()
        return {"status": "success"}
