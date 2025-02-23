"""KQML message handling module."""
from datetime import datetime
from loguru import logger
from typing import Dict, Any

class KQMLMessage:
    def __init__(self, performative: str, content: Any, sender: str, receiver: str):
        if not content or str(content).strip() == "":
            raise ValueError("Content cannot be empty")
        self.performative = performative
        self.content = content
        self.sender = sender
        self.receiver = receiver

    def to_dict(self) -> Dict[str, Any]:
        return {
            "performative": self.performative,
            "content": self.content,
            "sender": self.sender,
            "receiver": self.receiver
        }

    def to_string(self) -> str:
        """Convert message to KQML string format."""
        return f"({self.performative} {self.content} :sender {self.sender} :receiver {self.receiver})"

    @classmethod
    def from_string(cls, kqml_string: str) -> 'KQMLMessage':
        # Improved parsing logic
        parts = kqml_string.strip('()').split()
        if len(parts) < 4:
            raise ValueError("Invalid KQML message format")
        
        performative = parts[0]
        try:
            sender_index = parts.index(':sender')
            receiver_index = parts.index(':receiver')
        except ValueError:
            raise ValueError("Missing :sender or :receiver in KQML message")
        
        content = ' '.join(parts[1:sender_index])
        if not content:
            raise ValueError("Content cannot be empty")
        
        sender = parts[sender_index + 1]
        receiver = parts[receiver_index + 1]
        
        return cls(performative, content, sender, receiver)

def generate_synthetic_kqml(performative: str, content: str, sender: str, receiver: str) -> str:
    return f"({performative} {content} :sender {sender} :receiver {receiver})"

async def process_message(message: str) -> dict:
    """Process a KQML message."""
    start_time = datetime.now()
    try:
        parsed_msg = KQMLMessage.from_string(message)
        result = parsed_msg.to_dict()
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            "Successfully processed KQML message",
            extra={
                "type": "kqml",
                "data": {
                    "performative": result.get("performative"),
                    "sender": result.get("sender"),
                    "receiver": result.get("receiver"),
                    "process_time_ms": process_time
                }
            }
        )
        return result
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.exception(
            "Failed to process KQML message",
            extra={
                "type": "kqml",
                "data": {
                    "raw_message": message,
                    "error": str(e),
                    "process_time_ms": process_time
                }
            }
        )
        raise

# Example usage
if __name__ == "__main__":
    # Generate a synthetic KQML message
    synthetic_msg = generate_synthetic_kqml("tell", "temperature 25", "sensor1", "agent1")
    print(f"Synthetic KQML: {synthetic_msg}")

    # Parse the synthetic message
    parsed_msg = KQMLMessage.from_string(synthetic_msg)
    print(f"Parsed message: {parsed_msg.to_dict()}")