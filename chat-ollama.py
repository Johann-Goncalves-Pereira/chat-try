import requests

# Open-WebUI API endpoint
WEBUI_URL = "http://localhost:3000/api/chat"


# Function to send a message to an LLM
def ask_model(model_name, message):
    response = requests.post(
        WEBUI_URL,
        json={"model": model_name, "messages": [{"role": "user", "content": message}]},
    )
    return response.json()["message"]


def chat():
    print("Welcome to the chat! Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        llama_response = ask_model("llama3", user_input)
        print("Llama 3.3:", llama_response)

        gemma_response = ask_model("gemma2", llama_response)
        print("Gemma 2:", gemma_response)


if __name__ == "__main__":
    chat()
