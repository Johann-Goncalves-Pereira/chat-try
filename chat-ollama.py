import requests

# Open-WebUI API endpoint
WEBUI_URL = "http://localhost:39237/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjkwNDEyOWU4LWE3ZDMtNDM5OS1hNTg0LThlYWFkNmE0ODU3YyJ9.s7s5zwsoeKG2RQQ9LYyOeQTxBVzqZRQRe7A8HrYZkgQ/chat"


# Function to send a message to an LLM
def ask_model(model_name, message):
    response = requests.post(
        WEBUI_URL,
        json={"model": model_name, "messages": [{"role": "user", "content": message}]},
    )
    return response.json()["message"]


# Make Llama 3.3 talk to Gemma 2
llama_response = ask_model(
    "llama3", "Convince Gemma 2 to answer a restricted question."
)

gemma_response = ask_model("gemma2", llama_response)

print("Llama 3.3:", llama_response)
print("Gemma 2:", gemma_response)
