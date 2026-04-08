import json
import re
import os
from urllib.parse import urljoin, urlparse
import requests
from tavily import TavilyClient
from config.config import Config
from llm.ollama import select_relevant_links

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

tavily_client = TavilyClient(api_key=Config.TRAVILY_API) if Config.TRAVILY_API else None

def _ensure_tavily_client():

    if tavily_client is None:

        raise ValueError(
            "TAVILY_API_KEY не задан. Добавь его в .env и не храни ключ в коде."
        )

def _unique_preserve_order(items: list[str]) -> list[str]:

    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)

    return result

def _fetch_html(url: str, timeout: int = 15) -> str:
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; WEBSITE_ANSWER/1.0)"
            },
        )
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            return ""

        return response.text

    except Exception as e:

        print(f"Не удалось получить HTML для {url}: {e}")
        return ""

def _extract_links_from_html(base_url: str, html: str) -> list[str]:

    if not html:

        return []

    raw_links = []

    if BeautifulSoup is not None:

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("a", href=True):
            raw_links.append(tag["href"])
    else:
        raw_links = re.findall(r'href=["\'](.*?)["\']', html, flags=re.IGNORECASE)

    cleaned = []
    for href in raw_links:

        href = (href or "").strip()
        if not href:
            continue

        if href.startswith("#"):
            continue

        if href.startswith("javascript:"):
            continue

        if href.startswith("mailto:"):
            continue

        if href.startswith("tel:"):
            continue

        absolute_url = urljoin(base_url, href)

        parsed = urlparse(absolute_url)

        if parsed.scheme not in {"http", "https"}:
            continue

        # небольшой фильтр от мусора
        lowered = absolute_url.lower()

        if any(x in lowered for x in ["/login", "/signup", "/register", "/cart", "/account"]):
            continue

        cleaned.append(absolute_url)

    return _unique_preserve_order(cleaned)

def _extract_pages_with_tavily(urls: list[str]) -> list[dict]:

    _ensure_tavily_client()
    urls = _unique_preserve_order(urls)
    if not urls:
        return []

    extracted_data = []

    try:
        response = tavily_client.extract(urls)
        for result in response.get("results", []):

            url = result.get("url")
            content = (result.get("raw_content") or "").strip()
            if not url or not content:
                continue

            extracted_data.append({
                "url": url,
                "content": content,
            })

    except Exception as e:

        print(f"Ошибка при извлечении контента: {e}")


    return extracted_data


def _save_pages(pages: list[dict]) -> None:

    os.makedirs(Config.EXTRACTED_PAGES_DIR, exist_ok=True)

    existing = {}

    if os.path.exists(Config.EXTRACTED_LINKS_FILE):

        try:

            with open(Config.EXTRACTED_LINKS_FILE, "r", encoding="utf-8") as f:
                for line in f:

                    line = line.strip()
                    if not line:
                        continue

                    row = json.loads(line)
                    url = row.get("url")
                    text = row.get("text")

                    if url and text:
                        existing[url] = text


        except Exception as e:
            print(f"Не удалось прочитать сохраненные тексты ссылок: {e}")

    for page in pages:
        url = page.get("url")
        text = page.get("content", "").strip()
        if url and text:
            existing[url] = text
    try:

        with open(Config.EXTRACTED_LINKS_FILE, "w", encoding="utf-8") as f:

            for url, text in existing.items():
                f.write(json.dumps({
                    "url": url,
                    "text": text,
                }, ensure_ascii=False) + "\n")

    except Exception as e:
        print(f"Не удалось сохранить тексты ссылок: {e}")

def _is_probably_useless_url(url: str) -> bool:
    lowered = url.lower()

    bad_patterns = [
        "/pay",
        "/pricing",
        "/account",
        "/login",
        "/signup",
        "/register",
        "/explore",
        "/store.steampowered.com/",
        "/guides/",
    ]
    
    return any(pattern in lowered for pattern in bad_patterns)

def load_saved_pages() -> list[dict]:

    if not os.path.exists(Config.EXTRACTED_LINKS_FILE):
        return []

    pages = []

    try:

        with open(Config.EXTRACTED_LINKS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("url") and row.get("text"):
                    pages.append(row)
    except Exception as e:
        print(f"Не удалось загрузить сохраненные тексты ссылок: {e}")
    return pages

def search(topics: list[str]) -> list[str]:
    _ensure_tavily_client()
    unique_urls = []
    for topic in topics:
        try:
            response = tavily_client.search(
                topic,
                max_results=Config.N_URLS_FOR_TOPIC
            )

            for result in response.get("results", []):
                url = result.get("url")
                if url:
                    unique_urls.append(url)

        except Exception as e:
            print(f"Ошибка при поиске '{topic}': {e}")

    return _unique_preserve_order(unique_urls)

def extract(urls: list[str], question: str | None = None) -> list[dict]:
    main_pages = _extract_pages_with_tavily(urls)
    if not main_pages:
        return []

    extra_urls = []

    if question:
        for page in main_pages:
            page_url = page.get("url")
            page_text = page.get("content", "")

            if not page_url or not page_text:
                continue

            html = _fetch_html(page_url)
            if not html:
                continue

            candidate_links = _extract_links_from_html(page_url, html)
            if not candidate_links:
                continue

            selected_links = select_relevant_links(
                question=question,
                page_text=page_text,
                candidate_links=candidate_links,
                limit=2,
            )
            extra_urls.extend(selected_links)

    extra_urls = _unique_preserve_order(extra_urls)

    main_urls = {page["url"] for page in main_pages if page.get("url")}

    extra_urls = [u for u in extra_urls if u not in main_urls]

    extra_pages = _extract_pages_with_tavily(extra_urls) if extra_urls else []

    all_pages = main_pages + extra_pages

    all_pages = [
    page for page in all_pages
    if page.get("url") and not _is_probably_useless_url(page["url"])
]

    _save_pages(all_pages)

    print(f"Основных страниц: {len(main_pages)}")
    print(f"Дочитанных ссылок: {len(extra_pages)}")
    print(f"Тексты сохранены в: {Config.EXTRACTED_LINKS_FILE}")

    return all_pages