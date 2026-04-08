import re
from typing import List


def _normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _keyword_overlap_score(question: str, text: str) -> int:
    question_words = {
        word.lower()
        for word in re.findall(r"\w+", question)
        if len(word) >= 3
    }

    text_lower = text.lower()
    return sum(1 for word in question_words if word in text_lower)


def _looks_like_navigation_trash(text: str) -> bool:
    lowered = text.lower()

    trash_markers = [
        "sign in",
        "log in",
        "register",
        "privacy policy",
        "terms of service",
        "accept cookies",
        "all rights reserved",
        "shopping cart",
        "checkout",
    ]

    hits = sum(1 for marker in trash_markers if marker in lowered)
    return hits >= 3


def filter_pages(pages: List[dict], question: str, min_text_length: int = 500) -> List[dict]:
    filtered = []

    for page in pages:
        url = page.get("url")
        content = _normalize_text(page.get("content", ""))

        if not url or not content:
            print(f"[filter_pages] пропуск страницы без url/контента: {url}")
            continue

        if len(content) < min_text_length:
            print(f"[filter_pages] слишком короткая страница: {url}")
            continue

        if _looks_like_navigation_trash(content):
            print(f"[filter_pages] похоже на навигационный мусор: {url}")
            continue

        overlap_score = _keyword_overlap_score(question, content)
        if overlap_score == 0:
            print(f"[filter_pages] нет пересечения с вопросом: {url}")
            continue

        filtered.append({
            "url": url,
            "content": content,
        })

    return filtered