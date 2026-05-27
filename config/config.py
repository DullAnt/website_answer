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
DEFAULT_OLLAMA_REASONING = os.getenv("OLLAMA_REASONING", "false").lower() in {
    "1",
    "true",
    "yes",
}

# -------------------Device---------------------
DEFAULT_DEVICE = os.getenv("DEVICE", "cuda")

# -------------------Search---------------------
DEFAULT_TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
DEFAULT_SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "tavily")

# ------------------ Search Engine ------------------
DEFAULT_SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "tavily")

# ------------------ SearXNG ------------------
DEFAULT_SEARXNG_BASE_URL = os.getenv("SEARXNG_BASE_URL", "")
DEFAULT_SEARXNG_SEARCH_PATH = os.getenv("SEARXNG_SEARCH_PATH", "/search")
DEFAULT_SEARXNG_TIMEOUT = int(os.getenv("SEARXNG_TIMEOUT", "30"))
DEFAULT_SEARXNG_CATEGORIES = os.getenv("SEARXNG_CATEGORIES", "general")
DEFAULT_SEARXNG_LANGUAGE = os.getenv("SEARXNG_LANGUAGE", "auto")
DEFAULT_SEARXNG_SAFESEARCH = int(os.getenv("SEARXNG_SAFESEARCH", "0"))

# ------------------ Newton ------------------
DEFAULT_NEWTON_BASE_URL = os.getenv("NEWTON_BASE_URL", "https://newton.psbank.ru")
DEFAULT_NEWTON_SEARCH_PATH = os.getenv("NEWTON_SEARCH_PATH", "/api/internal/search/resultByGroups")
DEFAULT_NEWTON_TIMEOUT = int(os.getenv("NEWTON_TIMEOUT", "30"))
DEFAULT_NEWTON_WHERE = os.getenv("NEWTON_WHERE", "iblock_wiki")
DEFAULT_NEWTON_ROOT_SECTION_ID = os.getenv("NEWTON_ROOT_SECTION_ID", "0")
DEFAULT_NEWTON_COOKIE = os.getenv("NEWTON_COOKIE", "")
DEFAULT_NEWTON_VERIFY_SSL = os.getenv("NEWTON_VERIFY_SSL", "true").lower() in {"1", "true", "yes"}


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
    OLLAMA_REASONING = DEFAULT_OLLAMA_REASONING

    # Embeddings
    EMBEDDING_MODEL = DEFAULT_EMBEDDING_MODEL

    # Travily
    TRAVILY_API = DEFAULT_TAVILY_API_KEY
    # Search Engine
    SEARCH_ENGINE = DEFAULT_SEARCH_ENGINE

    # SearXNG
    SEARXNG_BASE_URL = DEFAULT_SEARXNG_BASE_URL
    SEARXNG_SEARCH_PATH = DEFAULT_SEARXNG_SEARCH_PATH
    SEARXNG_TIMEOUT = DEFAULT_SEARXNG_TIMEOUT
    SEARXNG_CATEGORIES = DEFAULT_SEARXNG_CATEGORIES
    SEARXNG_LANGUAGE = DEFAULT_SEARXNG_LANGUAGE
    SEARXNG_SAFESEARCH = DEFAULT_SEARXNG_SAFESEARCH

     # Newton
    NEWTON_BASE_URL = DEFAULT_NEWTON_BASE_URL
    NEWTON_SEARCH_PATH = DEFAULT_NEWTON_SEARCH_PATH
    NEWTON_TIMEOUT = DEFAULT_NEWTON_TIMEOUT
    NEWTON_WHERE = DEFAULT_NEWTON_WHERE
    NEWTON_ROOT_SECTION_ID = DEFAULT_NEWTON_ROOT_SECTION_ID
    NEWTON_COOKIE = DEFAULT_NEWTON_COOKIE
    NEWTON_VERIFY_SSL = DEFAULT_NEWTON_VERIFY_SSL
        
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
    "DEFAULT_SEARCH_ENGINE",
    "DEFAULT_SEARXNG_BASE_URL",
    "DEFAULT_SEARXNG_SEARCH_PATH",
    "DEFAULT_SEARXNG_TIMEOUT",
    "DEFAULT_SEARXNG_CATEGORIES",
    "DEFAULT_SEARXNG_LANGUAGE",
    "DEFAULT_SEARXNG_SAFESEARCH",
    "DEFAULT_NEWTON_BASE_URL",
    "DEFAULT_NEWTON_SEARCH_PATH",
    "DEFAULT_NEWTON_TIMEOUT",
    "DEFAULT_NEWTON_WHERE",
    "DEFAULT_NEWTON_ROOT_SECTION_ID",
    "DEFAULT_NEWTON_COOKIE",
    "DEFAULT_NEWTON_VERIFY_SSL",
    "EXTRACTED_LINKS_FILE"
]
