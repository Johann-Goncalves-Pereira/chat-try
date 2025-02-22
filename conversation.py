from typing import List, Tuple, Optional
from dataclasses import replace
from models import Player, ConversationState, generate_context
from api_client import get_response

COLORS = {
    "player_one": "\033[32m",
    "player_two": "\033[33m",
    "master": "\033[37m",
    "reset": "\033[0m",
}


def clean_response(response: str, character_name: str) -> str:
    if response.startswith("Master:"):
        return ""
    if response.startswith(f"{character_name}:"):
        return response[len(character_name) + 1 :].strip()
    return response


def format_message(speaker: str, message: str, player1_name: str) -> str:
    color = COLORS.get(
        "master"
        if speaker == "Master"
        else "player_one"
        if speaker == player1_name
        else "player_two"
    )
    return f"{color}{speaker}: {message}{COLORS['reset']}"


def handle_player_turn(
    player: Player, other_player: Player, context: str
) -> Optional[str]:
    prompt = f"{context}\n\n{player.initial_prompt}"
    response = get_response(player.model, prompt)
    if response:
        return clean_response(response, player.name)
    return None


def update_conversation_history(
    state: ConversationState, speaker: str, message: str
) -> ConversationState:
    return replace(
        state,
        conversation_history=[*state.conversation_history, f"{speaker}: {message}"],
    )


def handle_player_response(
    state: ConversationState,
    current_player: Player,
    other_player: Player,
) -> Tuple[ConversationState, Optional[str]]:
    response = handle_player_turn(
        current_player,
        other_player,
        generate_context(current_player, other_player.name),
    )
    if response:
        print(format_message(current_player.name, response, state.player1.name))
        state = update_conversation_history(state, current_player.name, response)
    return state, response


def handle_master_input(
    state: ConversationState, master_comments: List[str]
) -> Tuple[ConversationState, str]:
    try:
        user_comment = input("Master, add a comment (or press Enter to skip): ").strip()
    except KeyboardInterrupt:
        print("\nGracefully exiting conversation...")
        exit(0)

    if user_comment:
        new_history = [*state.conversation_history, f"Master: {user_comment}"]
        new_state = replace(state, conversation_history=new_history)
        print(format_message("Master", user_comment, state.player1.name))
        return new_state, user_comment

    if state.comment_index < len(master_comments):
        comment = master_comments[state.comment_index]
        new_history = [*state.conversation_history, f"Master: {comment}"]
        new_state = replace(
            state,
            conversation_history=new_history,
            comment_index=state.comment_index + 1,
        )
        print(format_message("Master", comment, state.player1.name))
        return new_state, comment

    return state, ""


def handle_master_turn(
    state: ConversationState,
    master_comments: List[str],
    previous_response: Optional[str],
    update_player: Player,
) -> Tuple[ConversationState, Player]:
    state, master_response = handle_master_input(state, master_comments)
    updated_player = replace(
        update_player,
        initial_prompt=master_response if master_response else previous_response or "",
    )
    return state, updated_player


def process_conversation_turn(
    state: ConversationState, master_comments: List[str]
) -> ConversationState:
    # Player 1's turn
    state, response1 = handle_player_response(state, state.player1, state.player2)

    # Master's turn after Player 1
    state, player2 = handle_master_turn(
        state, master_comments, response1, state.player2
    )
    state = replace(state, player2=player2)

    # Player 2's turn
    state, response2 = handle_player_response(state, state.player2, state.player1)

    # Master's turn after Player 2
    state, player1 = handle_master_turn(
        state, master_comments, response2, state.player1
    )
    return replace(state, player1=player1)
