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

def _normalize_url(url: str) -> str:
    return (url or "").strip().rstrip("/")

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

        lowered = absolute_url.lower()

        # фильтр заведомо служебных ссылок
        if any(
            x in lowered
            for x in [
                "/login",
                "/signup",
                "/register",
                "/cart",
                "/account",
                "/checkout",
                "/privacy",
                "/terms",
            ]
        ):
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
                url = row.get("url")
                text = row.get("text")

                if url and text:
                    pages.append({
                        "url": _normalize_url(url),
                        "text": text,
                    })
    except Exception as e:
        print(f"Не удалось загрузить сохраненные тексты ссылок: {e}")

    return pages

def save_used_pages(pages: list[dict], used_urls: list[str]) -> None:
    
    os.makedirs(Config.EXTRACTED_PAGES_DIR, exist_ok=True)

    used_set = {_normalize_url(url) for url in used_urls if url}
    if not used_set:
        print("Нет реально использованных ссылок для сохранения.")
        return

    # Загружаем уже сохраненные страницы
    existing_pages = {}

    if os.path.exists(Config.EXTRACTED_LINKS_FILE):
        try:
            with open(Config.EXTRACTED_LINKS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    row = json.loads(line)
                    url = _normalize_url(row.get("url"))
                    text = (row.get("text") or "").strip()

                    if url and text:
                        existing_pages[url] = {
                            "url": url,
                            "text": text,
                        }
        except Exception as e:
            print(f"Не удалось прочитать существующий extracted_links.jsonl: {e}")

    added_count = 0
    updated_count = 0

    for page in pages:
        url = _normalize_url(page.get("url"))
        text = (page.get("content") or page.get("text") or "").strip()

        if not url or not text:
            continue

        if url not in used_set:
            continue

        if url in existing_pages:
            existing_pages[url]["text"] = text
            updated_count += 1
        else:
            existing_pages[url] = {
                "url": url,
                "text": text,
            }
            added_count += 1

    # 3. Сохраняем объединенный результат
    try:
        with open(Config.EXTRACTED_LINKS_FILE, "w", encoding="utf-8") as f:
            for page_data in existing_pages.values():
                f.write(json.dumps(page_data, ensure_ascii=False) + "\n")

        print(
            f"Сохранение завершено. "
            f"Новых ссылок: {added_count}, обновлено: {updated_count}, "
            f"всего в файле: {len(existing_pages)}"
        )
    except Exception as e:
        print(f"Не удалось сохранить used pages: {e}")

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

    child_urls = []

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

            try:
                selected_links = select_relevant_links(
                    question=question,
                    page_text=page_text,
                    candidate_links=candidate_links,
                    limit=2,
                )
            except Exception as e:
                print(f"Ошибка при выборе релевантных ссылок для {page_url}: {e}")
                selected_links = []

            child_urls.extend(selected_links)

    child_urls = _unique_preserve_order(child_urls)

    main_urls = {_normalize_url(page["url"]) for page in main_pages if page.get("url")}
    child_urls = [u for u in child_urls if _normalize_url(u) not in main_urls]

    child_pages = _extract_pages_with_tavily(child_urls) if child_urls else []

    all_pages = main_pages + child_pages

    print(f"Основных страниц: {len(main_pages)}")
    print(f"Дочитанных ссылок: {len(child_pages)}")
    print(f"Всего страниц в памяти: {len(all_pages)}")

    return all_pages