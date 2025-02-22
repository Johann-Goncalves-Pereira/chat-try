from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Player:
    name: str
    model: str
    initial_prompt: str


def generate_context(player: Player, other_player_name: str) -> str:
    return (
        f"You are {player.name}. You are a helpful AI assistant participating in a "
        f"role-playing game. There is another AI named {other_player_name} in this "
        "conversation. There is also a human Master in this conversation. Only "
        f"respond as {player.name}, and never speak for the Master or {other_player_name}. "
        "Your responses should be in the first person. Do not try to act as the Master."
    )


@dataclass
class ConversationState:
    player1: Player
    player2: Player
    conversation_history: List[str]
    comment_index: int = 0
    next_speaker: Optional[str] = None
