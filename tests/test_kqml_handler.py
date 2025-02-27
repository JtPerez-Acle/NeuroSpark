"""
This test file has been replaced by test_interaction_handler.py
"""
import pytest
from app.kqml_handler import process_interaction, generate_synthetic_interaction

# Skip all tests in this file since we've migrated to the interaction model
pytestmark = pytest.mark.skip(reason="KQML model replaced with AgentInteraction")