"""Tests for data generator module."""
import pytest
from datetime import datetime
from app.data_generator import DataGenerator

class TestDataGenerator:
    """Test cases for DataGenerator class."""

    def setup_method(self):
        """Set up test cases."""
        self.generator = DataGenerator()

    def test_create_agent_profile(self):
        """Test creating a single agent profile."""
        # Test with specific type and role
        profile = self.generator.create_agent_profile("sensor", "temperature")
        assert profile["type"] == "sensor"
        assert profile["role"] == "temperature"
        assert "created_at" in profile
        assert isinstance(profile["id"], str)
        
        # Test with random type and role
        profile = self.generator.create_agent_profile()
        assert profile["type"] in self.generator.agent_types
        assert profile["role"] in self.generator.agent_types[profile["type"]]

    def test_create_agent_profiles(self):
        """Test creating multiple agent profiles."""
        num_agents = 3
        profiles = self.generator.create_agent_profiles(num_agents)
        
        assert len(profiles) == num_agents
        for profile in profiles:
            assert "id" in profile
            assert "type" in profile
            assert "role" in profile
            assert "created_at" in profile

    def test_generate_content_by_type(self):
        """Test content generation for different agent types."""
        # Test sensor content
        content = self.generator.generate_content_by_type("sensor", "temperature")
        assert "reading" in content
        assert "temperature" in content
        assert "celsius" in content
        assert "timestamp" in content

        # Test analyzer content
        content = self.generator.generate_content_by_type("analyzer", "pattern")
        assert "analysis" in content
        assert "status" in content
        assert "confidence" in content
        assert "timestamp" in content

        # Test coordinator content
        content = self.generator.generate_content_by_type("coordinator", "system")
        assert "command" in content
        assert "action" in content
        assert "priority" in content
        assert "timestamp" in content

        # Test actuator content
        content = self.generator.generate_content_by_type("actuator", "hvac")
        assert "status" in content
        assert "action_status" in content
        assert "timestamp" in content

    def test_generate_interaction(self):
        """Test generating an interaction between agents."""
        sender = self.generator.create_agent_profile("sensor", "temperature")
        receiver = self.generator.create_agent_profile("analyzer", "pattern")
        
        interaction = self.generator.generate_interaction(sender, receiver)
        
        assert "interaction_id" in interaction
        assert "sender_id" in interaction
        assert "receiver_id" in interaction
        assert "topic" in interaction
        assert "message" in interaction
        assert "interaction_type" in interaction
        assert "timestamp" in interaction
        assert "metadata" in interaction

    def test_get_interaction_type_by_agent(self):
        """Test getting interaction types for different agent types."""
        sensor_type = self.generator.get_interaction_type_by_agent("sensor")
        assert sensor_type in ["report", "notification", "update"]
        
        analyzer_type = self.generator.get_interaction_type_by_agent("analyzer")
        assert analyzer_type in ["query", "report", "alert"]
        
        coordinator_type = self.generator.get_interaction_type_by_agent("coordinator")
        assert coordinator_type in ["command", "request", "broadcast"]
        
        actuator_type = self.generator.get_interaction_type_by_agent("actuator")
        assert actuator_type in ["response", "update", "notification"]

    def test_generate_synthetic_data(self):
        """Test generating a complete synthetic dataset."""
        num_agents = 3
        num_interactions = 5
        data = self.generator.generate_synthetic_data(num_agents, num_interactions)
        
        assert "agents" in data
        assert "interactions" in data
        assert len(data["agents"]) == num_agents
        assert len(data["interactions"]) == num_interactions
        
        # Verify agent structure
        for agent in data["agents"]:
            assert "id" in agent
            assert "type" in agent
            assert "role" in agent
            assert "created_at" in agent
        
        # Verify interaction structure
        for interaction in data["interactions"]:
            assert "interaction_id" in interaction
            assert "sender_id" in interaction
            assert "receiver_id" in interaction
            assert "topic" in interaction
            assert "message" in interaction
            assert "interaction_type" in interaction
            assert "timestamp" in interaction
            assert "metadata" in interaction
