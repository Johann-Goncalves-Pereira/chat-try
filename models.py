from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Player:
    name: str
    model: str
    initial_prompt: str


def generate_context(
    player: Player, players: List[Player], next_speaker: Optional[str] = None
) -> str:
    other_players = [p for p in players if p.name != player.name]
    other_players_str = ", ".join([p.name for p in other_players])

    context = (
        f"You are {player.name}. You are a helpful AI assistant participating in a role-playing game.\n"
        f"Your role is to embody {player.name} and respond in the first person.\n"
        f"Other AI participants include: {other_players_str}.\n"
        "There is also a human Master in this conversation.\n"
        f"Important: Only respond as {player.name}. Do not speak for the Master or any other AI. "
        "Do not try to act as the Master. Focus solely on your character's perspective and role."
    )

    if next_speaker:
        context += f"\nIt is now {next_speaker}'s turn to speak."

    return context


@dataclass
class ConversationState:
    players: List[Player]
    conversation_history: List[str]
    comment_index: int = 0
    next_speaker: Optional[str] = None
