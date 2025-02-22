import requests
import json

def get_ollama_response(model, prompt):
    url = "http://localhost:11434/api/generate"  # Ollama API endpoint
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return json.loads(response.text)["response"]
    else:
        return None

model1 = "crown/darkidol"
model2 = "gemma2"
prompt1 = "Hello, I am model 1."
prompt2 = ""
conversation_history = []

for i in range(5):  # Example: 5 turns
    response1 = get_ollama_response(model1, prompt1)
    if response1:
        print(f"{model1}: {response1}")
        conversation_history.append(f"{model1}: {response1}")
        prompt2 = response1
    response2 = get_ollama_response(model2, prompt2)
    if response2:
        print(f"{model2}: {response2}")
        conversation_history.append(f"{model2}: {response2}")
        prompt1 = response2

print("\n--- Conversation History ---")
for message in conversation_history:
    print(message)