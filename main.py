import logging
import random
from functools import reduce
from config import INITIAL_STATE_FILE, MAX_CONVERSATION_TURNS
from state_manager import load_initial_state
from conversation import process_conversation_turn
from models import ConversationState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_conversation_history(history: list[str]) -> None:
    """Print the entire conversation history."""
    print("\n\n--- Conversation History ---")
    for message in history:
        print(message)


def main() -> None:
    """Main function to run the conversation simulation."""
    try:
        initial_state = load_initial_state(INITIAL_STATE_FILE)
        players = initial_state.players  # your list of players
        initial_comment_index = 0
        master_comments = []  # Initialize as empty list or load from config

        # Choose a random starting player
        first_player = random.choice(players)

        state = ConversationState(
            players=players,
            conversation_history=[],
            comment_index=initial_comment_index,
            next_speaker=first_player.name,  # Set the initial speaker to the random player
        )

        # Process all turns using reduce
        final_state = reduce(
            lambda state, _: process_conversation_turn(state, master_comments),
            range(MAX_CONVERSATION_TURNS),
            state,
        )

        print_conversation_history(final_state.conversation_history)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
