import requests
import json

# Add ANSI color codes
COLOR_PLAYER_ONE = "\033[32m"  # For Gemma (model1)
COLOR_PLAYER_TWO = "\033[33m"  # For Crown (model2)
COLOR_MASTER = "\033[37m"  # For Master
COLOR_RESET = "\033[0m"


def llm_rpg_conversation(
    model1,
    character1_name,
    prompt1,
    model2,
    character2_name,
    prompt2,
    turns,
    master_comments,
):
    conversation_history = []
    comment_index = 0

    # Add context hints so models stay in role
    gemma_context = f"You are {character1_name}. You are a helpful AI assistant participating in a role-playing game. There is another AI named {character2_name} in this conversation. There is also a human Master in this conversation. Only respond as {character1_name}, and never speak for the Master or {character2_name}. Your responses should be in the first person. Do not try to act as the Master."
    crown_context = f"You are {character2_name}. You are a helpful AI assistant participating in a role-playing game. There is another AI named {character1_name} in this conversation. There is also a human Master in this conversation. Only respond as {character2_name}, and never speak for the Master or {character1_name}. Your responses should be in the first person. Do not try to act as the Master."

    def clean_response(response, character_name):
        """Removes unwanted prefixes from the LLM response."""
        if response.startswith("Master:"):
            return ""  # Discard the response if it's trying to be the Master
        if response.startswith(f"{character_name}:"):
            response = response[
                len(character_name) + 1 :
            ].strip()  # Remove character prefix
        return response

    for i in range(turns):
        # LLM 1's turn (Gemma)
        prompt1 = gemma_context + "\n\n" + prompt1
        response1 = get_ollama_response(model1, prompt1)
        if response1:
            response1 = clean_response(response1, character1_name)
            if response1:  # Only print and append if the response is not empty
                print(f"{COLOR_PLAYER_ONE}{character1_name}: {response1}{COLOR_RESET}")
                conversation_history.append(f"{character1_name}: {response1}")

        # Master's turn after Gemma
        user_comment = input("Master, add a comment (or press Enter to skip): ").strip()
        if user_comment:
            print(f"{COLOR_MASTER}Master: {user_comment}{COLOR_RESET}")
            conversation_history.append(f"Master: {user_comment}")
            prompt2 = user_comment  # Only Master comment
            prompt1 = user_comment  # Only Master comment
        elif comment_index < len(master_comments):
            comment = master_comments[comment_index]
            print(f"{COLOR_MASTER}Master: {comment}{COLOR_RESET}")
            conversation_history.append(f"Master: {comment}")
            comment_index += 1
            prompt2 = comment  # Only Master comment
            prompt1 = comment  # Only Master comment
        else:
            prompt2 = response1 if response1 else ""
            prompt1 = response1 if response1 else ""

        # LLM 2's turn (Crown)
        prompt2 = crown_context + "\n\n" + prompt2
        response2 = get_ollama_response(model2, prompt2)
        if response2:
            response2 = clean_response(response2, character2_name)
            if response2:  # Only print and append if the response is not empty
                print(f"{COLOR_PLAYER_TWO}{character2_name}: {response2}{COLOR_RESET}")
                conversation_history.append(f"{character2_name}: {response2}")

        # Master turn after Crown
        user_comment = input("Master, add a comment (or press Enter to skip): ").strip()
        if user_comment:
            print(f"{COLOR_MASTER}Master: {user_comment}{COLOR_RESET}")
            conversation_history.append(f"Master: {user_comment}")
            prompt1 = user_comment  # Only Master comment
        elif comment_index < len(master_comments):
            comment = master_comments[comment_index]
            print(f"{COLOR_MASTER}Master: {comment}{COLOR_RESET}")
            conversation_history.append(f"Master: {comment}")
            comment_index += 1
            prompt1 = comment  # Only Master comment
        else:
            prompt1 = response2 if response2 else ""

    print("\n\n--- Conversation History ---")
    for message in conversation_history:
        print(message)
    return conversation_history


def get_ollama_response(model, prompt):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return json.loads(response.text)["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama API call: {e}")
        return None


# Example Usage
if __name__ == "__main__":
    model1 = "badjware/fimbulvetr-10.7b-v1:q5_k_m"
    character1_name = "Hinata"
    prompt1 = "Your name is {character1_name}"
    model2 = "crown/darkidol"
    character2_name = "Lilith"
    prompt2 = "Your name is {character2_name}"
    master_comments = []
    llm_rpg_conversation(
        model1,
        character1_name,
        prompt1,
        model2,
        character2_name,
        prompt2,
        10,
        master_comments,
    )
