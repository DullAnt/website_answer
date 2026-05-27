from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config.config import Config
from search.base import BaseSearchEngine


class NewtonSearchEngine(BaseSearchEngine):
    """Search adapter for Newton's internal Bitrix-backed wiki results API."""

    def __init__(self):
        self.base_url = Config.NEWTON_BASE_URL.strip().rstrip("/") + "/"
        self.search_path = Config.NEWTON_SEARCH_PATH
        self.timeout = Config.NEWTON_TIMEOUT
        self.where = Config.NEWTON_WHERE
        self.root_section_id = Config.NEWTON_ROOT_SECTION_ID
        self.verify_ssl = Config.NEWTON_VERIFY_SSL
        self.max_results = Config.N_URLS_FOR_TOPIC

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "WEBSITE_ANSWER/1.0",
            "Referer": self.base_url + "wiki/",
        })
        if Config.NEWTON_COOKIE:
            self.session.headers["Cookie"] = Config.NEWTON_COOKIE

    def _search_url(self) -> str:
        return urljoin(self.base_url, self.search_path.lstrip("/"))

    @staticmethod
    def _text_from_html(value: str | None) -> str:
        return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)

    def _request_topic(self, topic: str) -> dict:
        response = self.session.get(
            self._search_url(),
            params={
                "q": topic,
                "where": self.where,
                "rootSectionId": self.root_section_id,
            },
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def _parse_pages(self, payload: dict) -> list[dict]:
        pages = []

        for group in payload.get("result", []):
            if not isinstance(group, dict):
                continue
            source_type = group.get("type")
            for item in group.get("data", []):
                if not isinstance(item, dict):
                    continue

                relative_url = item.get("URL_WO_PARAMS") or item.get("URL")
                url = urljoin(self.base_url, relative_url or "")
                title = self._text_from_html(item.get("TITLE_FORMATED") or item.get("TITLE"))
                content = self._text_from_html(item.get("BODY_FORMATED"))
                if not relative_url or not content:
                    continue

                pages.append({
                    "url": url,
                    "title": title or None,
                    "content": content,
                    "success": True,
                    "error": None,
                    "source_type": source_type,
                })

        return pages

    @staticmethod
    def _unique_pages(pages: list[dict]) -> list[dict]:
        result = []
        seen = set()
        for page in pages:
            url = page.get("url")
            if url and url not in seen:
                seen.add(url)
                result.append(page)
        return result

    def search_pages(self, topics: list[str]) -> list[dict]:
        pages = []
        for topic in topics:
            try:
                pages.extend(self._parse_pages(self._request_topic(topic)))
            except Exception as exc:
                print(f"[NewtonSearchEngine] Ошибка при поиске '{topic}': {exc}")
        return self._unique_pages(pages)

    def raw_search(self, query: str) -> dict:
        return self._request_topic(query)

    def search(self, topics: list[str]) -> list[str]:
        return [page["url"] for page in self.search_pages(topics)[:self.max_results]]