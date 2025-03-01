"""Tests for data generator module."""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Mock the logging before importing the module
with patch('app.monitoring.logging_config.setup_logging', MagicMock()):
    from app.data_generator import DataGenerator, PDScenarioGenerator, PPScenarioGenerator, PEScenarioGenerator, SARScenarioGenerator

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
            
    def test_scenario_generator_init(self):
        """Test initializing generator with a scenario."""
        # Test each scenario type
        generator_pd = DataGenerator(scenario="pd")
        assert generator_pd.scenario == "pd"
        assert generator_pd.scenario_generator is not None
        
        generator_pp = DataGenerator(scenario="predator_prey")
        assert generator_pp.scenario == "predator_prey"
        assert generator_pp.scenario_generator is not None
        
        generator_pe = DataGenerator(scenario="pursuer_evader")
        assert generator_pe.scenario == "pursuer_evader"
        assert generator_pe.scenario_generator is not None
        
        generator_sar = DataGenerator(scenario="search_rescue")
        assert generator_sar.scenario == "search_rescue"
        assert generator_sar.scenario_generator is not None
        
        # Test invalid scenario
        generator_invalid = DataGenerator(scenario="invalid")
        assert generator_invalid.scenario == "invalid"
        assert generator_invalid.scenario_generator is None
        
    def test_generate_scenario_data(self):
        """Test generating scenario-based data."""
        # Test Prisoners' Dilemma scenario
        generator = DataGenerator(scenario="pd")
        data = generator.generate_scenario_data(5, 10, rounds=3)
        
        assert "agents" in data
        assert "interactions" in data
        assert "run_id" in data
        assert "scenario" in data
        assert data["scenario"] == "prisoners_dilemma"
        assert len(data["agents"]) == 5
        assert len(data["interactions"]) <= 10  # May be less due to round limits
        
        # Check agent structure
        for agent in data["agents"]:
            assert agent["type"] == "prisoner"
            assert agent["role"] in ["cooperator", "defector", "tit_for_tat", "random"]
            assert "strategy" in agent
            assert "score" in agent
            assert "history" in agent
            
        # Check interaction structure
        for interaction in data["interactions"]:
            assert interaction["interaction_type"] in ["cooperate", "defect"]
            assert "metadata" in interaction
            assert "scenario" in interaction["metadata"]
            assert "round" in interaction["metadata"]
            assert "sender_decision" in interaction["metadata"]
            assert "receiver_decision" in interaction["metadata"]
            
    def test_scenario_generators(self):
        """Test each scenario generator directly."""
        # Test Prisoners' Dilemma scenario generator
        pd_generator = PDScenarioGenerator()
        pd_data = pd_generator.generate_data(3, 10, rounds=2)
        assert len(pd_data["agents"]) == 3
        assert pd_data["scenario"] == "prisoners_dilemma"
        
        # Test Predator/Prey scenario generator
        pp_generator = PPScenarioGenerator()
        pp_data = pp_generator.generate_data(9, 5)  # 3 predators, 6 prey
        assert len(pp_data["agents"]) == 9
        assert len(pp_data["interactions"]) == 5
        assert pp_data["scenario"] == "predator_prey"
        
        # Test Pursuer/Evader scenario generator
        pe_generator = PEScenarioGenerator()
        pe_data = pe_generator.generate_data(6, 8, time_steps=4)  # 2 pursuers, 4 evaders
        assert len(pe_data["agents"]) == 6
        assert len(pe_data["interactions"]) <= 8
        assert pe_data["scenario"] == "pursuer_evader"
        
        # Test Search and Rescue scenario generator
        sar_generator = SARScenarioGenerator()
        sar_data = sar_generator.generate_data(10, 12)  # Mixture of searchers, coordinators, victims
        assert len(sar_data["agents"]) == 10
        assert len(sar_data["interactions"]) == 12
        assert sar_data["scenario"] == "search_rescue"
