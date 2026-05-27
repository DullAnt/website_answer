from config.config import Config


def get_search_engine():
    engine_name = getattr(Config, "SEARCH_ENGINE", "searxng").lower()

    if engine_name == "tavily":
        from search.tavily_search import TavilySearchEngine

        return TavilySearchEngine()

    if engine_name == "searxng":
        from search.searxng import SearxngSearchEngine

        return SearxngSearchEngine()

    if engine_name == "newton":
        from search.newton import NewtonSearchEngine

        return NewtonSearchEngine()

    raise ValueError(f"Неизвестный SEARCH_ENGINE: {engine_name}")