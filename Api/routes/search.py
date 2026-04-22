import requests
from fastapi import APIRouter, HTTPException

from Api.schemas import (
    SearchLinksRequest,
    SearchLinksResponse,
    SearchRawRequest,
    SearchRawResponse,
)
from config.config import Config
from search.searxng import SearxngSearchEngine

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/links", response_model=SearchLinksResponse)
def search_links(payload: SearchLinksRequest):
    try:
        engine = SearxngSearchEngine()
        urls = engine.search(payload.topics)

        return SearchLinksResponse(
            urls=urls[:payload.max_results]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка поиска ссылок: {str(e)}"
        )


@router.post("/raw", response_model=SearchRawResponse)
def search_raw(payload: SearchRawRequest):
    try:
        base_url = getattr(Config, "SEARXNG_BASE_URL", "").strip().rstrip("/")
        search_path = getattr(Config, "SEARXNG_SEARCH_PATH", "/search")
        timeout = getattr(Config, "SEARXNG_TIMEOUT", 30)

        if not base_url:
            raise ValueError("SEARXNG_BASE_URL не задан в Config")

        response = requests.get(
            f"{base_url}{search_path}",
            params={
                "q": payload.query,
                "format": "json",
                "categories": getattr(Config, "SEARXNG_CATEGORIES", "general"),
                "language": getattr(Config, "SEARXNG_LANGUAGE", "auto"),
                "safesearch": int(getattr(Config, "SEARXNG_SAFESEARCH", 0)),
            },
            timeout=timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": "WEBSITE_ANSWER_API/1.0",
            },
        )

        response.raise_for_status()

        return SearchRawResponse(
            query=payload.query,
            results=response.json()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка raw-поиска: {str(e)}"
        )