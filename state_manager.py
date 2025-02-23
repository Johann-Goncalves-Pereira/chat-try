import json
import logging
from pathlib import Path
from models import Player, ConversationState

logger = logging.getLogger(__name__)


def load_initial_state(file_path: Path) -> ConversationState:
    """Load the initial conversation state from a JSON file."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        players = [Player(**player_data) for player_data in data["players"]]
        return ConversationState(
            players=players,
            conversation_history=data["conversation_history"],
            comment_index=data["comment_index"],
        )
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading initial state: {e}")
        raise
