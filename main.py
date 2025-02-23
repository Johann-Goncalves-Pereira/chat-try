import json
from models import Player, ConversationState
from conversation import process_conversation_turn
from functools import reduce


def load_initial_state(file_path: str) -> ConversationState:
    """Loads the initial state from a JSON file."""
    with open(file_path, "r") as f:
        data = json.load(f)
    player1 = Player(**data["player1"])
    player2 = Player(**data["player2"])
    return ConversationState(
        player1=player1,
        player2=player2,
        conversation_history=data["conversation_history"],
        comment_index=data["comment_index"],
    )


def main():
    initial_state = load_initial_state("initial_state.json")

    master_comments = []

    # Process all turns using reduce
    final_state = reduce(
        lambda state, _: process_conversation_turn(state, master_comments),
        range(50),
        initial_state,
    )

    print("\n\n--- Conversation History ---")
    for message in final_state.conversation_history:
        print(message)


if __name__ == "__main__":
    main()
