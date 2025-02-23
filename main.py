import logging
from functools import reduce
from config import INITIAL_STATE_FILE, MAX_CONVERSATION_TURNS
from state_manager import load_initial_state
from conversation import process_conversation_turn

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
        master_comments = []

        # Process all turns using reduce
        final_state = reduce(
            lambda state, _: process_conversation_turn(state, master_comments),
            range(MAX_CONVERSATION_TURNS),
            initial_state,
        )

        print_conversation_history(final_state.conversation_history)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
