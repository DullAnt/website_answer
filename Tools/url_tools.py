from typing import List


def _normalize_url(url: str) -> str:
    return (url or "").strip().rstrip("/")


def _is_probably_useless_url(url: str) -> bool:
    lowered = _normalize_url(url).lower()

    bad_exact = {
        "https://iwillplay.ru",
        "https://store.steampowered.com",
        "https://store.steampowered.com/explore",
        "https://www.polygon.com/guides",
    }

    bad_patterns = [
        "/pay",
        "/pricing",
        "/account",
        "/login",
        "/signup",
        "/register",
        "/checkout",
        "/cart",
        "/explore",
        "/privacy",
        "/terms",
        "/support",
        "/contact",
        "/about",
        "/tag/",
        "/category/",
    ]

    if lowered in bad_exact:
        return True

    return any(pattern in lowered for pattern in bad_patterns)


def filter_urls(urls: List[str]) -> List[str]:
    filtered = []
    seen = set()

    for url in urls:
        normalized = _normalize_url(url)
        if not normalized:
            continue

        if normalized in seen:
            continue
        seen.add(normalized)

        if _is_probably_useless_url(normalized):
            print(f"[filter_urls] удален URL: {normalized}")
            continue

        filtered.append(normalized)

    return filtered