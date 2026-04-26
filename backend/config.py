import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is missing. Please set it in the .env file.")

class Config:
    CHROMA_PATH = "./chroma_db"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    LLM_MODEL = "claude-sonnet-4-5"
    ANTHROPIC_API_KEY = ANTHROPIC_API_KEY

config = Config()
