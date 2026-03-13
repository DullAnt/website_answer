import os
from dotenv import load_dotenv

from typing import Literal

load_dotenv()

# Typing parameters
LLM_ANSWER_PARSER_TYPE = Literal["none", "json", "string"]


#------------------Ollama-----------------------------------------------
DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "600"))
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:2b")


# -------------------Device---------------------
DEFAULT_DEVICE = os.getenv("DEVICE", "cuda")

# -------------------Travily---------------------
DEFAULT_TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")

#----------------Embendings------------------
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

#------------------RAG parametres---------------------------------
DEFAULT_TOP_K = int(os.getenv("TOP_K", "3"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

#------------------PATHS---------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
FAISS_DB_DIR = os.path.join(BASE_DIR, "faiss_data")


class Config:

    #Ollama    
    OLLAMA_HOST = DEFAULT_OLLAMA_HOST
    OLLAMA_MODEL = DEFAULT_OLLAMA_MODEL
    DEVICE = DEFAULT_DEVICE

    # Embeddings
    EMBEDDING_MODEL = DEFAULT_EMBEDDING_MODEL

    # Travily
    TRAVILY_API = DEFAULT_TAVILY_API_KEY
    
    # RAG
    TOP_K = DEFAULT_TOP_K
    SIMILARITY_THRESHOLD = DEFAULT_SIMILARITY_THRESHOLD

    # PATHS
    BASE_DIR = BASE_DIR
    PROMPTS_DIR = PROMPTS_DIR
    FAISS_DB_DIR = FAISS_DB_DIR

__all__ = [
    "Config",
    "DEFAULT_OLLAMA_MODEL",
    "DEFAULT_OLLAMA_HOST",
    "EMBEDDING_MODELS",
    "DEFAULT_OLLAMA_TIMEOUT",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_TOP_K",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_DEVICE",
    "DEFAULT_TAVILY_API_KEY",
    "BASE_DIR",
    "PROMPTS_DIR",
    "FAISS_DB_DIR"
]
