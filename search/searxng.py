import requests

from config.config import Config
from search.base import BaseSearchEngine


class SearxngSearchEngine(BaseSearchEngine):
    def __init__(self):
        self.base_url = getattr(Config, "SEARXNG_BASE_URL", "").strip().rstrip("/")
        self.search_path = getattr(Config, "SEARXNG_SEARCH_PATH", "/search")
        self.timeout = getattr(Config, "SEARXNG_TIMEOUT", 30)
        self.max_results = Config.N_URLS_FOR_TOPIC
        self.categories = getattr(Config, "SEARXNG_CATEGORIES", "general").strip()
        self.language = getattr(Config, "SEARXNG_LANGUAGE", "auto").strip()
        self.safesearch = int(getattr(Config, "SEARXNG_SAFESEARCH", 0))

        if not self.base_url:
            raise ValueError("SEARXNG_BASE_URL не задан в Config.")

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "WEBSITE_ANSWER/1.0",
        })

    @staticmethod
    def _normalize_url(url: str) -> str:
        return (url or "").strip().rstrip("/")

    @staticmethod
    def _unique_preserve_order(items: list[str]) -> list[str]:
        seen = set()
        result = []

        for item in items:
            normalized = SearxngSearchEngine._normalize_url(item)
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)

        return result

    def _build_search_url(self) -> str:
        return f"{self.base_url}{self.search_path}"

    def _search_one_topic(self, topic: str) -> list[str]:
        try:
            response = self.session.get(
                self._build_search_url(),
                params={
                    "q": topic,
                    "format": "json",
                    "categories": self.categories,
                    "language": self.language,
                    "safesearch": self.safesearch,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            urls = []
            for item in results:
                if not isinstance(item, dict):
                    continue

                url = item.get("url")
                if url:
                    urls.append(url)

            return self._unique_preserve_order(urls)[:self.max_results]

        except Exception as e:
            print(f"[SearxngSearchEngine] Ошибка при поиске '{topic}': {e}")
            return []

    def search(self, topics: list[str]) -> list[str]:
        all_urls = []

        for topic in topics:
            topic_urls = self._search_one_topic(topic)
            all_urls.extend(topic_urls)

        return self._unique_preserve_order(all_urls)