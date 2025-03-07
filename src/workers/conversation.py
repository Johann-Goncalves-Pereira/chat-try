from typing import List, Tuple, Optional
from dataclasses import replace
import random
from src.workers.models import Player, ConversationState, PlayerStats, generate_context
from lib.api_client import get_response
from prompt_toolkit import prompt
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.box import ROUNDED

console = Console()

COLORS = {
    "master": "white",
    "reset": "",
}

PLAYER_COLORS = [
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
]


def clean_response(response: str, character_name: str) -> str:
    if response.startswith("Master:"):
        return ""
    if response.startswith(f"{character_name}:"):
        return response[len(character_name) + 1 :].strip()
    return response


def format_message(
    speaker: str, message: str, first_player_name: str, state: ConversationState
) -> str:
    if speaker == "Master":
        color = COLORS["master"]
    else:
        try:
            player_index = next(
                i for i, p in enumerate(state.players) if p.name == speaker
            )
            color = PLAYER_COLORS[
                player_index % len(PLAYER_COLORS)
            ]  # Cycle through colors
        except StopIteration:
            color = PLAYER_COLORS[0]  # Default

    formatted_message = Panel(
        f"[{color}]{escape(speaker)}: {escape(message)}[/{color}]",
        title=f"[{color}]{escape(speaker)}[/{color}]",
        border_style=color,
        box=ROUNDED,
    )
    return formatted_message


def handle_player_turn(
    player: Player, players: List[Player], context: str, conversation_history: List[str]
) -> Optional[str]:
    # Include a relevant portion of the conversation history in the prompt
    history_length = min(5, len(conversation_history))  # Adjust as needed
    recent_history = "\n".join(conversation_history[-history_length:])
    prompt = (
        f"{context}\nConversation History:\n{recent_history}\n\n{player.initial_prompt}"
    )
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
    other_players: List[Player],
) -> Tuple[ConversationState, Optional[str]]:
    response = handle_player_turn(
        current_player,
        state.players,
        generate_context(current_player, state.players, state.next_speaker),
        state.conversation_history,
    )
    if response:
        console.print(
            format_message(current_player.name, response, state.players[0].name, state)
        )
        state = update_conversation_history(state, current_player.name, response)
    return state, response


def handle_master_input(
    state: ConversationState, master_comments: List[str]
) -> Tuple[ConversationState, str]:
    try:
        user_comment = prompt(
            "Master, add a comment (or press Enter to skip): "
        ).strip()
        # Clear the line containing the prompt
        print("\033[F\033[K", end="")
    except KeyboardInterrupt:
        print("\nGracefully exiting conversation...")
        exit(0)

    if user_comment:
        new_history = [*state.conversation_history, f"Master: {user_comment}"]
        console.print(
            format_message("Master", user_comment, state.players[0].name, state)
        )
        new_state = replace(state, conversation_history=new_history)
        return new_state, user_comment

    if state.comment_index < len(master_comments):
        comment = master_comments[state.comment_index]
        new_history = [*state.conversation_history, f"Master: {comment}"]
        new_state = replace(
            state,
            conversation_history=new_history,
            comment_index=state.comment_index + 1,
        )
        console.print(format_message("Master", comment, state.players[0].name, state))
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


def get_mentioned_player(message: str, players: List[Player]) -> Optional[Player]:
    """Returns the mentioned player or None if no player is mentioned."""
    for player in players:
        if f"@{player.name.lower()}" in message.lower():
            return player
    return None


def get_opposite_player(
    current: Player, players: List[Player], player_stats: dict[str, PlayerStats]
) -> Player:
    """Returns a randomly selected eligible player based on turn constraints."""
    MAX_TURNS_WITHOUT_PLAY = 3  # Reduced from 5 to 3 for more frequent rotation

    # Update turns without play for all players except current
    for player in players:
        if player != current:
            player_stats[player.name].increment_without_play()

    # First priority: Players who haven't played for MAX_TURNS_WITHOUT_PLAY or more turns
    must_include = [
        p
        for p in players
        if p != current
        and player_stats[p.name].turns_without_play >= MAX_TURNS_WITHOUT_PLAY
    ]
    if must_include:
        selected = random.choice(must_include)
        player_stats[selected.name].reset_without_play()
        player_stats[selected.name].increment_consecutive()
        return selected

    # Second priority: Players with the highest turns_without_play
    if len(players) > 2:  # Only apply for conversations with more than 2 players
        max_turns_without = max(
            player_stats[p.name].turns_without_play for p in players if p != current
        )
        most_waiting = [
            p
            for p in players
            if p != current
            and player_stats[p.name].turns_without_play == max_turns_without
        ]
        if most_waiting and player_stats[most_waiting[0].name].consecutive_turns < 2:
            selected = random.choice(most_waiting)
            player_stats[selected.name].reset_without_play()
            player_stats[selected.name].increment_consecutive()
            return selected

    # Third priority: Regular eligible players
    eligible_players = [
        p
        for p in players
        if p != current and player_stats[p.name].consecutive_turns < 2
    ]

    if not eligible_players:
        # Reset consecutive turns if no eligible players
        for player in players:
            player_stats[player.name].reset_consecutive()
        eligible_players = [p for p in players if p != current]

    selected = random.choice(eligible_players)
    player_stats[selected.name].reset_without_play()
    player_stats[selected.name].increment_consecutive()
    return selected


def determine_next_speaker(
    master_response: str, current_player: Player, state: ConversationState
) -> Optional[str]:
    """Determines the next speaker based on mentions or turn order."""
    mentioned_player = get_mentioned_player(master_response, state.players)
    if mentioned_player:
        return mentioned_player.name
    return get_opposite_player(current_player, state.players, state.player_stats).name


def handle_complete_turn(
    state: ConversationState, current_player: Player, master_comments: List[str]
) -> Tuple[ConversationState, Optional[str]]:
    """Handles a complete turn cycle: player response + master turn."""
    other_players = [p for p in state.players if p != current_player]

    # Handle player's response
    state, response = handle_player_response(state, current_player, other_players)

    # Determine the next player
    next_player = get_opposite_player(current_player, state.players, state.player_stats)

    # Handle master's turn, updating the next player's prompt
    state, updated_player = handle_master_turn(
        state, master_comments, response, next_player
    )

    # Update the player in the state
    updated_players = [updated_player if p == next_player else p for p in state.players]
    state = replace(state, players=updated_players)

    return state, updated_player.initial_prompt


def process_conversation_turn(
    state: ConversationState, master_comments: List[str]
) -> ConversationState:
    # Initialize player stats if not present
    if not hasattr(state, "player_stats"):
        state = replace(
            state,
            player_stats={player.name: PlayerStats(player) for player in state.players},
        )

    # Handle explicitly set next speaker (from @mentions)
    if state.next_speaker:
        current_player = next(
            (p for p in state.players if p.name == state.next_speaker), None
        )
        if not current_player:
            print(f"Warning: next_speaker {state.next_speaker} not found.")
            current_player = state.players[0]

        state, master_response = handle_complete_turn(
            state, current_player, master_comments
        )
        next_speaker = determine_next_speaker(master_response, current_player, state)
        return replace(state, next_speaker=next_speaker)

    # Normal random flow with constraints
    current_player = (
        state.players[0]
        if not state.next_speaker
        else next(p for p in state.players if p.name == state.next_speaker)
    )

    state, master_response = handle_complete_turn(
        state, current_player, master_comments
    )

    if master_response and "@" in master_response:
        next_speaker = determine_next_speaker(master_response, current_player, state)
    else:
        next_player = get_opposite_player(
            current_player, state.players, state.player_stats
        )
        next_speaker = next_player.name

    return replace(state, next_speaker=next_speaker)
