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
DEFAULT_N_URLS_FOR_TOPIC = int(os.getenv("N_URLS_FOR_TOPIC", "10"))  # сколько URL брать на 1 topic
DEFAULT_BATCH_URL = int(os.getenv("BATCH_URL", "4"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

#------------------PATHS---------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
FAISS_DB_DIR = os.path.join(BASE_DIR, "faiss_data")
DATA_DIR = os.path.join(BASE_DIR, "data")
EXTRACTED_PAGES_DIR = os.path.join(DATA_DIR, "extracted_pages")
EXTRACTED_LINKS_FILE = os.path.join(EXTRACTED_PAGES_DIR, "extracted_links.jsonl")

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
    N_URLS_FOR_TOPIC = DEFAULT_N_URLS_FOR_TOPIC
    BATCH_URL = DEFAULT_BATCH_URL
    SIMILARITY_THRESHOLD = DEFAULT_SIMILARITY_THRESHOLD

    # PATHS
    BASE_DIR = BASE_DIR
    PROMPTS_DIR = PROMPTS_DIR
    FAISS_DB_DIR = FAISS_DB_DIR
    DATA_DIR = DATA_DIR
    EXTRACTED_PAGES_DIR = EXTRACTED_PAGES_DIR
    EXTRACTED_LINKS_FILE = EXTRACTED_LINKS_FILE

__all__ = [
    "Config",
    "DEFAULT_OLLAMA_MODEL",
    "DEFAULT_OLLAMA_HOST",
    "DEFAULT_OLLAMA_TIMEOUT",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_TOP_K",
    "DEFAULT_N_URLS_FOR_TOPIC",
    "DEFAULT_BATCH_URL",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_DEVICE",
    "DEFAULT_TAVILY_API_KEY",
    "BASE_DIR",
    "PROMPTS_DIR",
    "FAISS_DB_DIR",
    "DATA_DIR",
    "EXTRACTED_PAGES_DIR",
    "EXTRACTED_LINKS_FILE",
]
