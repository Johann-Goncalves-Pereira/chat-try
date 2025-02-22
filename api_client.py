import requests
import json
from typing import Optional
from functools import partial


def get_ollama_response(base_url: str, model: str, prompt: str) -> Optional[str]:
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return json.loads(response.text)["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama API call: {e}")
        return None


# Partial application for easier usage
get_response = partial(get_ollama_response, "http://localhost:11434")
