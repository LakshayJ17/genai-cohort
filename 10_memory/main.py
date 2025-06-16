# flake8 : noqa

from mem0 import Memory
from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small"
        }
    },
    "llm": {"provider": "openai", "config": {"api_key": OPENAI_API_KEY}}
}

mem_client = Memory.from_config(config)
