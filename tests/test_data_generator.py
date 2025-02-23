import pytest
from app.data_generator import DataGenerator

class TestDataGenerator:
    @pytest.fixture
    def data_generator(self):
        return DataGenerator()

    def test_create_agent_profiles(self, data_generator):
        """Test that agent profiles are created correctly."""
        profiles = data_generator.create_agent_profiles()
        assert len(profiles) > 0
        assert all(isinstance(p, dict) for p in profiles)
        assert all("id" in p and "role" in p for p in profiles)

    @pytest.mark.asyncio
    async def test_generate_measurement(self, data_generator):
        """Test measurement message generation."""
        msg = await data_generator.generate_measurement()
        assert isinstance(msg, dict)
        assert all(k in msg for k in ["sender", "receiver", "performative", "content"])
        assert msg["performative"] == "tell"
        assert any(word in msg["content"] for word in ["celsius", "percent"])

    @pytest.mark.asyncio
    async def test_generate_analysis_result(self, data_generator):
        """Test analysis result message generation."""
        msg = await data_generator.generate_analysis_result()
        assert isinstance(msg, dict)
        assert all(k in msg for k in ["sender", "receiver", "performative", "content"])
        assert msg["performative"] == "inform"
        assert "status" in msg["content"]

    @pytest.mark.asyncio
    async def test_generate_action_result(self, data_generator):
        """Test action result message generation."""
        msg = await data_generator.generate_action_result()
        assert isinstance(msg, dict)
        assert all(k in msg for k in ["sender", "receiver", "performative", "content"])
        assert msg["performative"] == "tell"
        assert "action_complete" in msg["content"]

    @pytest.mark.asyncio
    async def test_generate_coordinator_message(self, data_generator):
        """Test coordinator message generation."""
        msg = await data_generator.generate_coordinator_message()
        assert isinstance(msg, dict)
        assert all(k in msg for k in ["sender", "receiver", "performative", "content"])
        assert msg["performative"] == "request"
        assert any(cmd in msg["content"] for cmd in ["set_temperature", "set_light_level", "set_ventilation"])
        assert any(str(num) in msg["content"] for num in range(0, 101))

    @pytest.mark.asyncio
    async def test_generate_interaction(self, data_generator):
        """Test random interaction generation."""
        msg = await data_generator.generate_interaction()
        assert isinstance(msg, dict)
        assert all(k in msg for k in ["sender", "receiver", "performative", "content"])

    @pytest.mark.asyncio
    async def test_generate_synthetic_data(self, data_generator):
        """Test synthetic data generation."""
        data = await data_generator.generate_synthetic_data(num_agents=3, num_messages=5)
        assert isinstance(data, dict)
        assert "agents" in data
        assert "interactions" in data
        assert len(data["agents"]) == 3
        assert len(data["interactions"]) == 5
