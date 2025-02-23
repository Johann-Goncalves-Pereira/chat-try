import requests
import json
import logging
from functools import partial
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaAPIError(Exception):
    """Custom exception for Ollama API errors."""

    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_ollama_response(base_url: str, model: str, prompt: str) -> str:
    """Send a request to Ollama API with retry logic."""
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        return json.loads(response.text)["response"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during Ollama API call: {e}")
        raise OllamaAPIError(f"Failed to get response from Ollama: {e}")


# Create a partial function with default base URL
get_response = partial(get_ollama_response, "http://localhost:11434")
