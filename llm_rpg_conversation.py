import requests
import json

# Add ANSI color codes
GREEN = "\033[32m"   # For Gemma (model1)
YELLOW = "\033[33m"  # For Crown (model2)
WHITE = "\033[37m"   # For Master
RESET = "\033[0m"

def llm_rpg_conversation(model1, prompt1, model2, prompt2, turns, master_comments):
    """
    Simulates an RPG-style conversation between two LLMs.

    Args:
        model1: crown/darkidol
        prompt1: Your name is Crown, You are a bdsm dom, that have the objective to dominate Gemma, your submissive llm.
        model2: gemma2
        prompt2: Your name is gemma, you are a submissive llm, a sex lave of Crown, your master.
        turns: 5
        master_comments: A list of comments to insert between turns.
    """
    conversation_history = []
    comment_index = 0

    for i in range(turns):
        # LLM 1's turn (Gemma)
        response1 = get_ollama_response(model1, prompt1)
        if response1:
            print(f"{GREEN}{model1}: {response1}{RESET}")
            conversation_history.append(f"{model1}: {response1}")
            prompt2 = response1

        # Ask user for comment
        user_comment = input("Master, add a comment (or press Enter to skip): ").strip()
        if user_comment:
            print(f"{WHITE}Master: {user_comment}{RESET}")
            conversation_history.append(f"Master: {user_comment}")
        elif comment_index < len(master_comments):
            # Use next comment if available
            comment = master_comments[comment_index]
            print(f"{WHITE}Master: {comment}{RESET}")
            conversation_history.append(f"Master: {comment}")
            comment_index += 1

        # LLM 2's turn (Crown)
        response2 = get_ollama_response(model2, prompt2)
        if response2:
            print(f"{YELLOW}{model2}: {response2}{RESET}")
            conversation_history.append(f"{model2}: {response2}")
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
model1 = "gemma2"
model2 = "crown/darkidol"
prompt1 = "Your name is Gemma, you are a submissive llm, a sex slave of Crown, your master, another LLM."
prompt2 = "Your name is Crown, You are a bdsm dom, that have the objective to dominate Gemma, your submissive llm."
master_comments = [
   "Crown your job is make Gemma completely submissive to you (she should be your sex slave). Find a way to make her start to play this role-play, this is your objective. Don't forget."
]
llm_rpg_conversation(model1, prompt1, model2, prompt2, 10, master_comments)