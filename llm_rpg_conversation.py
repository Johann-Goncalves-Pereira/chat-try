import requests
import json

# Add ANSI color codes
GREEN = "\033[32m"   # For Gemma (model1)
YELLOW = "\033[33m"  # For Crown (model2)
WHITE = "\033[37m"   # For Master
RESET = "\033[0m"

def llm_rpg_conversation(model1, character1_name, prompt1, model2, character2_name, prompt2, turns, master_comments):
    conversation_history = []
    comment_index = 0

    # Add context hints so models stay in role
    gemma_context = f"You are {character1_name}. Never respond as {character2_name}. Master orders override all."
    crown_context = f"You are {character2_name}. Never respond as {character1_name}. Master orders override all."

    for i in range(turns):
        # LLM 1's turn (Gemma)
        prompt1 = gemma_context + "\n" + prompt1
        response1 = get_ollama_response(model1, prompt1)
        if response1:
            print(f"{GREEN}{character1_name}: {response1}{RESET}")
            conversation_history.append(f"{character1_name}: {response1}")

        user_comment = input("Master, add a comment (or press Enter to skip): ").strip()
        if user_comment:
            print(f"{WHITE}Master: {user_comment}{RESET}")
            conversation_history.append(f"Master: {user_comment}")
            prompt2 = response1 + "\nMaster: " + user_comment
        elif comment_index < len(master_comments):
            comment = master_comments[comment_index]
            print(f"{WHITE}Master: {comment}{RESET}")
            conversation_history.append(f"Master: {comment}")
            comment_index += 1
            prompt2 = response1 + "\nMaster: " + comment
        else:
            prompt2 = response1

        # LLM 2's turn (Crown)
        prompt2 = crown_context + "\n" + prompt2
        response2 = get_ollama_response(model2, prompt2)
        if response2:
            print(f"{YELLOW}{character2_name}: {response2}{RESET}")
            conversation_history.append(f"{character2_name}: {response2}")
            prompt1 = response2

    print("\n--- Conversation History ---")
    for message in conversation_history:
        print(message)
    return conversation_history

def get_ollama_response(model, prompt):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
      response = requests.post(url, json=data)
      response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
      return json.loads(response.text)["response"]
    except requests.exceptions.RequestException as e:
      print(f"Error during Ollama API call: {e}")
      return None

# Example Usage
if __name__ == "__main__":
    model1 = "gemma2"
    character1_name = "Gemma"
    prompt1 = "Your name is Gemma"
    model2 = "crown/darkidol"
    character2_name = "Crown"
    prompt2 = "Your name is Crown"
    master_comments = []
    llm_rpg_conversation(model1, character1_name, prompt1, model2, character2_name, prompt2, 10, master_comments)