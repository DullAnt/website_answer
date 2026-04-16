from config.config import Config
from search.tavily_search import TavilySearchEngine
from search.searxng import SearxngSearchEngine


def get_search_engine():
    engine_name = getattr(Config, "SEARCH_ENGINE", "tavily").lower()

    if engine_name == "tavily":
        return TavilySearchEngine()

    if engine_name == "searxng":
        return SearxngSearchEngine()

    raise ValueError(f"Неизвестный SEARCH_ENGINE: {engine_name}")