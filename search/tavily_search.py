from tavily import TavilyClient
from config.config import Config
from search.base import BaseSearchEngine


class TavilySearchEngine(BaseSearchEngine):
    def __init__(self):
        api_key = getattr(Config, "TRAVILY_API", None) or getattr(Config, "TAVILY_API_KEY", None)
        if not api_key:
            raise ValueError("Tavily API key не найден в Config.")

        self.client = TavilyClient(api_key=api_key)
        self.max_results = Config.N_URLS_FOR_TOPIC

    @staticmethod
    def _normalize_url(url: str) -> str:
        return (url or "").strip().rstrip("/")

    @staticmethod
    def _unique_preserve_order(items: list[str]) -> list[str]:
        seen = set()
        result = []

        for item in items:
            normalized = TavilySearchEngine._normalize_url(item)
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)

        return result

    def search(self, topics: list[str]) -> list[str]:
        unique_urls = []

        for topic in topics:
            try:
                response = self.client.search(
                    topic,
                    max_results=self.max_results
                )

                for result in response.get("results", []):
                    url = result.get("url")
                    if url:
                        unique_urls.append(url)

            except Exception as e:
                print(f"[TavilySearchEngine] Ошибка при поиске '{topic}': {e}")

        return self._unique_preserve_order(unique_urls)