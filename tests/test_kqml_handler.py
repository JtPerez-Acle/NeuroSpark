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