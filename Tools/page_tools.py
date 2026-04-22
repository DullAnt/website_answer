from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


def _normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def extract_page_content(
    url: str,
    timeout: int = 20,
    max_chars: int = 30000,
) -> dict:
    """
    Извлекает title и чистый текст страницы.
    Используется API-роутом /api/extract/pages.
    """

    if not _is_valid_url(url):
        return {
            "url": url,
            "title": None,
            "content": None,
            "success": False,
            "error": "Invalid URL",
        }

    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()

        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return {
                "url": url,
                "title": None,
                "content": None,
                "success": False,
                "error": f"Unsupported content type: {content_type}",
            }

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup([
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "form",
            "header",
            "footer",
            "nav",
            "aside",
        ]):
            tag.decompose()

        title = None
        if soup.title and soup.title.string:
            title = _normalize_text(soup.title.string)

        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("body")
            or soup
        )

        text = main.get_text(separator="\n", strip=True)
        text = _normalize_text(text)

        if max_chars and len(text) > max_chars:
            text = text[:max_chars].strip()

        if not text:
            return {
                "url": response.url,
                "title": title,
                "content": None,
                "success": False,
                "error": "Empty page content",
            }

        return {
            "url": response.url,
            "title": title,
            "content": text,
            "success": True,
            "error": None,
        }

    except requests.RequestException as e:
        return {
            "url": url,
            "title": None,
            "content": None,
            "success": False,
            "error": f"Request error: {str(e)}",
        }

    except Exception as e:
        return {
            "url": url,
            "title": None,
            "content": None,
            "success": False,
            "error": f"Extract error: {str(e)}",
        }


def _normalize_page(page: dict) -> dict:
    url = page.get("url") or page.get("source") or page.get("link")
    title = page.get("title")
    content = page.get("content") or page.get("text") or page.get("page_content")

    success = page.get("success")
    if success is None:
        success = bool(url and content)

    return {
        "url": url,
        "title": title,
        "content": content,
        "success": bool(success),
        "error": page.get("error"),
    }


def filter_pages(
    pages_or_urls: list,
    question: str | None = None,
    min_content_chars: int = 500,
    timeout: int = 20,
    max_chars: int = 30000,
) -> list[dict]:
    

    filtered_pages = []

    for item in pages_or_urls:
        if isinstance(item, str):
            page = extract_page_content(
                url=item,
                timeout=timeout,
                max_chars=max_chars,
            )
        elif isinstance(item, dict):
            page = _normalize_page(item)
        else:
            continue

        content = page.get("content") or ""

        if not page.get("success"):
            continue

        if len(content) < min_content_chars:
            continue

        filtered_pages.append(page)

    return filtered_pages