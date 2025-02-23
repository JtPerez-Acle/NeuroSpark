from typing import Dict, Any

class KQMLMessage:
    def __init__(self, performative: str, content: Any, sender: str, receiver: str):
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

    @classmethod
    def from_string(cls, kqml_string: str) -> 'KQMLMessage':
        # Improved parsing logic
        parts = kqml_string.strip('()').split()
        if len(parts) < 4:
            raise ValueError("Invalid KQML message format")
        
        performative = parts[0]
        sender_index = parts.index(':sender')
        receiver_index = parts.index(':receiver')
        
        content = ' '.join(parts[1:sender_index])
        sender = parts[sender_index + 1]
        receiver = parts[receiver_index + 1]
        
        return cls(performative, content, sender, receiver)

def generate_synthetic_kqml(performative: str, content: str, sender: str, receiver: str) -> str:
    return f"({performative} {content} :sender {sender} :receiver {receiver})"

# Example usage
if __name__ == "__main__":
    # Generate a synthetic KQML message
    synthetic_msg = generate_synthetic_kqml("tell", "temperature 25", "sensor1", "agent1")
    print(f"Synthetic KQML: {synthetic_msg}")

    # Parse the synthetic message
    parsed_msg = KQMLMessage.from_string(synthetic_msg)
    print(f"Parsed message: {parsed_msg.to_dict()}")