import requests
from fastapi import APIRouter

from config.config import Config

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def healthcheck():
    return {
        "status": "ok",
        "service": "Website Answer API"
    }


@router.get("/searxng")
def searxng_healthcheck():
    base_url = getattr(Config, "SEARXNG_BASE_URL", "").strip().rstrip("/")

    if not base_url:
        return {
            "status": "error",
            "message": "SEARXNG_BASE_URL не задан"
        }

    try:
        response = requests.get(
            f"{base_url}/search",
            params={"q": "test", "format": "json"},
            timeout=10,
        )

        return {
            "status": "ok" if response.ok else "error",
            "status_code": response.status_code,
            "searxng_url": base_url,
        }

    except Exception as e:
        return {
            "status": "error",
            "searxng_url": base_url,
            "message": str(e),
        }