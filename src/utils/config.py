from pathlib import Path

BASE_DIR = Path(__file__).parent
INITIAL_STATE_FILE = BASE_DIR / "initial_state.json"
OLLAMA_BASE_URL = "http://localhost:11434"
MAX_CONVERSATION_TURNS = 50
