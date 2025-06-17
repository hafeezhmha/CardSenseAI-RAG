import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()
dotenv_path = find_dotenv()

client = OpenAI()

def load_system_prompt():
    """Loads the system prompt from the markdown file."""
    try:
        with open("cardsense_system_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: `cardsense_system_prompt.md` not found.")
        print("Please make sure the system prompt file is in the same directory.")
        exit(1)

system_prompt = load_system_prompt() 