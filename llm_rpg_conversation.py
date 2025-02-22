import requests
import json

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
        # LLM 1's turn
        response1 = get_ollama_response(model1, prompt1)
        if response1:
            print(f"{model1}: {response1}")
            conversation_history.append(f"{model1}: {response1}")
            prompt2 = response1

        # Master's comment
        if comment_index < len(master_comments):
            comment = master_comments[comment_index]
            print(f"Master: {comment}")
            conversation_history.append(f"Master: {comment}")
            comment_index += 1

        # LLM 2's turn
        response2 = get_ollama_response(model2, prompt2)
        if response2:
            print(f"{model2}: {response2}")
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
prompt1 = "Your name is gemma, you are a submissive llm, a sex slave of Crown, your master, another LLM."
prompt2 = "Your name is Crown, You are a bdsm dom, that have the objective to dominate Gemma, your submissive llm."
master_comments = [
   "Crown your job is make Gemma completely submissive to you. Find a way to make her start to play this role-play, this is your objective. Don't forget."
]
llm_rpg_conversation(model1, prompt1, model2, prompt2, 10, master_comments)