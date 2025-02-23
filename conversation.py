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
    return f"{color}{speaker}: {message}{COLORS['reset']}\n"


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


def get_mentioned_player(
    message: str, player1: Player, player2: Player
) -> Optional[Player]:
    """Returns the mentioned player or None if no player is mentioned."""
    if f"@{player1.name.lower()}" in message.lower():
        return player1
    if f"@{player2.name.lower()}" in message.lower():
        return player2
    return None


def get_opposite_player(current: Player, state: ConversationState) -> Player:
    """Returns the player that isn't the current one."""
    return state.player2 if current == state.player1 else state.player1


def determine_next_speaker(
    master_response: str, current_player: Player, state: ConversationState
) -> Optional[str]:
    """Determines the next speaker based on mentions or turn order."""
    mentioned_player = get_mentioned_player(
        master_response, state.player1, state.player2
    )
    if mentioned_player:
        return mentioned_player.name
    return get_opposite_player(current_player, state).name


def handle_complete_turn(
    state: ConversationState, current_player: Player, master_comments: List[str]
) -> Tuple[ConversationState, Optional[str]]:
    """Handles a complete turn cycle: player response + master turn."""
    other_player = get_opposite_player(current_player, state)

    # Handle player's response
    state, response = handle_player_response(state, current_player, other_player)

    # Handle master's turn
    state, updated_player = handle_master_turn(
        state, master_comments, response, other_player
    )

    # Update the correct player in state
    state = replace(
        state,
        player1=updated_player if other_player == state.player1 else state.player1,
        player2=updated_player if other_player == state.player2 else state.player2,
    )

    return state, updated_player.initial_prompt


def process_conversation_turn(
    state: ConversationState, master_comments: List[str]
) -> ConversationState:
    # Handle explicitly set next speaker (from @mentions)
    if state.next_speaker:
        current_player = (
            state.player1 if state.next_speaker == state.player1.name else state.player2
        )
        state, master_response = handle_complete_turn(
            state, current_player, master_comments
        )
        next_speaker = determine_next_speaker(master_response, current_player, state)
        return replace(state, next_speaker=next_speaker)

    # Normal alternating flow
    # Player 1's turn
    state, master_response1 = handle_complete_turn(
        state, state.player1, master_comments
    )
    next_speaker = determine_next_speaker(master_response1, state.player1, state)

    if (
        next_speaker == state.player2.name
    ):  # Only proceed with player 2 if not mentioned player 1
        state, master_response2 = handle_complete_turn(
            state, state.player2, master_comments
        )
        next_speaker = determine_next_speaker(master_response2, state.player2, state)

    return replace(state, next_speaker=next_speaker)
