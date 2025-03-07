from dataclasses import dataclass, field
from typing import List, Dict, Optional


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


class PlayerStats:
    def __init__(self, player: Player):
        self.player = player
        self.consecutive_turns = 0
        self.turns_without_play = 0

    def reset_consecutive(self):
        self.consecutive_turns = 0

    def increment_consecutive(self):
        self.consecutive_turns += 1

    def increment_without_play(self):
        self.turns_without_play += 1

    def reset_without_play(self):
        self.turns_without_play = 0


@dataclass
class ConversationState:
    players: List[Player]
    conversation_history: List[str]
    comment_index: int = 0
    next_speaker: Optional[str] = None
    player_stats: Dict[str, PlayerStats] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize player_stats if empty
        if not self.player_stats:
            self.player_stats = {
                player.name: PlayerStats(player) for player in self.players
            }

    def add_message(self, message: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append(message)

    def increment_index(self) -> None:
        """Increment the comment index."""
        self.comment_index += 1
