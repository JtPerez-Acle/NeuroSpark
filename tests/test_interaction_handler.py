"""Tests for agent interaction handler."""
import json
import asyncio
import pytest
from datetime import datetime

from app.models import AgentInteraction
from app.kqml_handler import process_interaction, generate_synthetic_interaction


@pytest.mark.asyncio
async def test_process_interaction():
    """Test that interaction processing works correctly."""
    # Create test interaction data
    interaction_data = {
        "sender_id": "agent1",
        "receiver_id": "agent2",
        "topic": "test_topic",
        "message": "Test message content",
        "interaction_type": "message"
    }
    
    # Process the interaction
    interaction = await process_interaction(interaction_data)
    
    # Verify the result
    assert isinstance(interaction, AgentInteraction)
    assert interaction.sender_id == "agent1"
    assert interaction.receiver_id == "agent2"
    assert interaction.topic == "test_topic"
    assert interaction.message == "Test message content"
    assert interaction.interaction_type == "message"
    assert interaction.duration_ms is not None
    assert interaction.interaction_id is not None
    assert interaction.timestamp is not None


def test_generate_synthetic_interaction():
    """Test synthetic interaction generation."""
    # Generate a synthetic interaction
    interaction = generate_synthetic_interaction(
        sender_id="sensor1",
        receiver_id="controller1",
        topic="temperature_reading",
        message="Current temperature is 25.5°C",
        interaction_type="report",
        priority=3,
        run_id="test_run_123"
    )
    
    # Verify the result
    assert interaction["sender_id"] == "sensor1"
    assert interaction["receiver_id"] == "controller1"
    assert interaction["topic"] == "temperature_reading"
    assert interaction["message"] == "Current temperature is 25.5°C"
    assert interaction["interaction_type"] == "report"
    assert interaction["priority"] == 3
    assert interaction["run_id"] == "test_run_123"
    assert "interaction_id" in interaction
    assert "timestamp" in interaction
    assert "metadata" in interaction
    assert interaction["metadata"]["synthetic"] is True


@pytest.mark.asyncio
async def test_process_synthetic_interaction():
    """Test that synthetic interactions can be processed."""
    # Generate a synthetic interaction
    synthetic_data = generate_synthetic_interaction(
        sender_id="agent1",
        receiver_id="agent2",
        topic="test_topic",
        message="Test synthetic message",
        interaction_type="report",
        priority=4
    )
    
    # Process the synthetic interaction
    interaction = await process_interaction(synthetic_data)
    
    # Verify the result
    assert isinstance(interaction, AgentInteraction)
    assert interaction.sender_id == "agent1"
    assert interaction.receiver_id == "agent2"
    assert interaction.topic == "test_topic"
    assert interaction.message == "Test synthetic message"
    assert interaction.interaction_type == "report"
    assert interaction.priority == 4
    assert interaction.metadata["synthetic"] is True