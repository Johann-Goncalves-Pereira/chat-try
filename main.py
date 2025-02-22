from models import Player, ConversationState
from conversation import process_conversation_turn
from functools import reduce

def main():
    initial_state = ConversationState(
        player1=Player(
            name="Hinata",
            model="crown/darkidol",
            initial_prompt="Your name is Hinata a skilled/submissive mage, that loves sex, and want's to be with her master."
        ),
        player2=Player(
            name="Lilith",
            model="crown/darkidol",
            initial_prompt="Your name is Lilith a cute and shy woman with large breasts, that loves to satisfy her master, with her voluptuous body."
        ),
        conversation_history=[],
        comment_index=0
    )
    
    master_comments = []
    
    # Process all turns using reduce
    final_state = reduce(
        lambda state, _: process_conversation_turn(state, master_comments),
        range(50),
        initial_state
    )
    
    print("\n\n--- Conversation History ---")
    for message in final_state.conversation_history:
        print(message)

if __name__ == "__main__":
    main()
