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
        
        assert "id" in interaction
        assert "source_id" in interaction
        assert "target_id" in interaction
        assert "performative" in interaction
        assert "content" in interaction
        assert "kqml_content" in interaction
        assert "timestamp" in interaction
        
        # Verify KQML message format
        kqml_msg = interaction["kqml_content"]
        assert isinstance(kqml_msg, str)
        assert ":sender" in kqml_msg
        assert ":receiver" in kqml_msg
        assert ":content" in kqml_msg
        assert ":language" in kqml_msg
        assert ":ontology" in kqml_msg

    def test_get_performative_by_type(self):
        """Test getting performatives for different agent types."""
        sensor_perf = self.generator.get_performative_by_type("sensor")
        assert sensor_perf in ["tell", "inform"]
        
        analyzer_perf = self.generator.get_performative_by_type("analyzer")
        assert analyzer_perf in ["evaluate", "inform"]
        
        coordinator_perf = self.generator.get_performative_by_type("coordinator")
        assert coordinator_perf in ["achieve", "request"]
        
        actuator_perf = self.generator.get_performative_by_type("actuator")
        assert actuator_perf in ["tell", "inform"]

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
            assert "id" in interaction
            assert "source_id" in interaction
            assert "target_id" in interaction
            assert "performative" in interaction
            assert "content" in interaction
            assert "kqml_content" in interaction
            assert "timestamp" in interaction
