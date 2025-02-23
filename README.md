# Chat-Try: Ollama Chat Playground with Multiple AI Characters

## Description

Chat-Try is a Python-based project that simulates a conversation between multiple AI characters, each with a defined role and personality, within an RPG context. It leverages the Ollama API for generating character responses and allows for human "Master" input to guide the conversation.

## Features

- **Multi-character conversation simulation:** Simulates conversations between multiple AI characters.
- **RPG context:** Characters are defined with specific roles and personalities.
- **Ollama API integration:** Uses Ollama to generate character responses.
- **Master control:** Allows a human "Master" to influence the conversation.
- **Turn-based conversation management:** Manages the conversation flow and determines the next speaker.
- **Conversation history:** Tracks and prints the entire conversation history.
- **Configurable:** Loads initial state from a JSON file.
- **Turn Management:** Uses constraints to determine the next speaker, preventing any single character from dominating the conversation.
- **Rich Console Output:** Uses the `rich` library to format the conversation output with colors and panels.

## Dependencies

- [logging](https://docs.python.org/3/library/logging.html)
- [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/en/stable/)
- [requests](https://requests.readthedocs.io/en/latest/)
- [rich](https://rich.readthedocs.io/en/stable/)
- [tenacity](https://tenacity.readthedocs.io/)

## Installation

1.  Make sure you have Python 3.13 installed.
2.  Clone the repository.
3.  Install the dependencies using pip:

    ```bash
    pip install -r pyproject.toml
    ```

## Configuration

The initial state of the conversation, including the characters and their initial prompts, is loaded from [initial_state.json](http://_vscodecontentref_/2). Modify this file to customize the characters and their roles.

## Usage

Run the [main.py](http://_vscodecontentref_/3) script to start the conversation simulation:

```bash
python main.py
```

## Project Structure

```markdown
.
├── README.md # This file
├── main.py # Main script to run the simulation
├── pyproject.toml # Project dependencies
├── src/ # Source code directory
│ ├── utils/ # Utility functions and configuration
│ │ ├── config.py # Configuration settings
│ │ ├── initial_state.json # Initial conversation state
│ │ └── state_manager.py # Loads the initial state
│ └── workers/ # Modules for conversation and models
│ ├── conversation.py # Handles the conversation logic
│ └── models.py # Data models for players and conversation state
└── lib/
└── api_client.py # Handles communication with the Ollama API
```
