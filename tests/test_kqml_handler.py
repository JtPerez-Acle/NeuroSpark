import pytest
from app.kqml_handler import KQMLMessage, generate_synthetic_kqml

class TestKQMLHandler:
    def test_generate_synthetic_kqml(self):
        result = generate_synthetic_kqml("tell", "temperature 25", "sensor1", "agent1")
        assert result == "(tell temperature 25 :sender sensor1 :receiver agent1)"

    def test_kqml_message_from_string(self):
        kqml_string = "(tell temperature 25 :sender sensor1 :receiver agent1)"
        message = KQMLMessage.from_string(kqml_string)
        assert message.performative == "tell"
        assert message.content == "temperature 25"
        assert message.sender == "sensor1"
        assert message.receiver == "agent1"

    def test_kqml_message_to_dict(self):
        message = KQMLMessage("ask", "current humidity", "agent1", "sensor2")
        result = message.to_dict()
        expected = {
            "performative": "ask",
            "content": "current humidity",
            "sender": "agent1",
            "receiver": "sensor2"
        }
        assert result == expected

    def test_kqml_message_from_string_with_spaces(self):
        kqml_string = "(  tell   temperature 25   :sender   sensor1   :receiver   agent1  )"
        message = KQMLMessage.from_string(kqml_string)
        assert message.performative == "tell"
        assert message.content == "temperature 25"
        assert message.sender == "sensor1"
        assert message.receiver == "agent1"

    def test_kqml_message_from_string_with_complex_content(self):
        kqml_string = "(tell (temperature 25.5 humidity 60%) :sender sensor1 :receiver agent1)"
        message = KQMLMessage.from_string(kqml_string)
        assert message.performative == "tell"
        assert message.content == "(temperature 25.5 humidity 60%)"
        assert message.sender == "sensor1"
        assert message.receiver == "agent1"

    def test_kqml_message_invalid_format(self):
        with pytest.raises(ValueError):
            KQMLMessage.from_string("not a valid kqml message")
        
        with pytest.raises(ValueError):
            KQMLMessage.from_string("(tell)")  # Missing required fields
        
        with pytest.raises(ValueError):
            KQMLMessage.from_string("(tell content)")  # Missing sender/receiver

    def test_kqml_message_with_special_characters(self):
        """Test KQML messages containing special characters."""
        content = "temperature: 25°C, humidity: 60%"
        message = KQMLMessage("tell", content, "sensor1", "agent1")
        kqml_string = message.to_string()
        parsed = KQMLMessage.from_string(kqml_string)
        assert parsed.content == content

        # Test with quotes and backslashes
        content = 'reading "high" temp\\humidity'
        message = KQMLMessage("tell", content, "sensor1", "agent1")
        kqml_string = message.to_string()
        parsed = KQMLMessage.from_string(kqml_string)
        assert parsed.content == content

    def test_kqml_message_with_nested_expressions(self):
        """Test KQML messages with nested expressions."""
        nested_content = "(and (temperature 25) (humidity 60) (pressure 1013))"
        message = KQMLMessage("tell", nested_content, "sensor1", "agent1")
        kqml_string = message.to_string()
        parsed = KQMLMessage.from_string(kqml_string)
        assert parsed.content == nested_content

        # Test deeply nested content
        deep_nested = "(if (> temperature 30) (and (alert high-temp) (activate cooling)))"
        message = KQMLMessage("achieve", deep_nested, "controller1", "actuator1")
        kqml_string = message.to_string()
        parsed = KQMLMessage.from_string(kqml_string)
        assert parsed.content == deep_nested

    def test_kqml_message_partial_fields(self):
        """Test KQML messages with partial sender/receiver information."""
        # Test with only sender
        with pytest.raises(ValueError):
            KQMLMessage.from_string("(tell status :sender agent1)")

        # Test with only receiver
        with pytest.raises(ValueError):
            KQMLMessage.from_string("(tell status :receiver agent2)")

        # Test with swapped order of sender/receiver
        kqml_string = "(tell status :receiver agent2 :sender agent1)"
        message = KQMLMessage.from_string(kqml_string)
        assert message.sender == "agent1"
        assert message.receiver == "agent2"

    def test_kqml_message_whitespace_handling(self):
        """Test KQML message parsing with various whitespace patterns."""
        messages = [
            "(tell\nstatus\n:sender\nagent1\n:receiver\nagent2)",  # newlines
            "(tell\tstatus\t:sender\tagent1\t:receiver\tagent2)",  # tabs
            "(tell status :sender agent1 :receiver agent2)",        # single spaces
            "(tell  status  :sender  agent1  :receiver  agent2)",   # double spaces
        ]
        
        for msg in messages:
            parsed = KQMLMessage.from_string(msg)
            assert parsed.performative == "tell"
            assert parsed.content == "status"
            assert parsed.sender == "agent1"
            assert parsed.receiver == "agent2"

    def test_kqml_message_empty_content(self):
        """Test KQML messages with empty content."""
        with pytest.raises(ValueError):
            KQMLMessage("tell", "", "agent1", "agent2")
        
        with pytest.raises(ValueError):
            KQMLMessage.from_string("(tell :sender agent1 :receiver agent2)")