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


def handle_master_input(
    state: ConversationState, master_comments: List[str]
) -> Tuple[ConversationState, str]:
    user_comment = input("Master, add a comment (or press Enter to skip): ").strip()

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


def process_conversation_turn(
    state: ConversationState, master_comments: List[str]
) -> ConversationState:
    # Player 1's turn
    response1 = handle_player_turn(
        state.player1,
        state.player2,
        generate_context(state.player1, state.player2.name),
    )
    if response1:
        print(format_message(state.player1.name, response1, state.player1.name))
        state = replace(
            state,
            conversation_history=[
                *state.conversation_history,
                f"{state.player1.name}: {response1}",
            ],
        )

    # Master's turn after Player 1
    state, master_response = handle_master_input(state, master_comments)
    player2 = replace(
        state.player2,
        initial_prompt=master_response if master_response else response1 or "",
    )
    state = replace(state, player2=player2)

    # Player 2's turn
    response2 = handle_player_turn(
        state.player2,
        state.player1,
        generate_context(state.player2, state.player1.name),
    )
    if response2:
        print(format_message(state.player2.name, response2, state.player1.name))
        state = replace(
            state,
            conversation_history=[
                *state.conversation_history,
                f"{state.player2.name}: {response2}",
            ],
        )

    # Master's turn after Player 2
    state, master_response = handle_master_input(state, master_comments)
    player1 = replace(
        state.player1,
        initial_prompt=master_response if master_response else response2 or "",
    )
    return replace(state, player1=player1)
