from fastapi import APIRouter, HTTPException

from Api.schemas import (
    ExtractPagesRequest,
    ExtractPagesResponse,
    ExtractedPage,
)
from Tools.page_tools import extract_page_content

router = APIRouter(prefix="/api/extract", tags=["extract"])


@router.post("/pages", response_model=ExtractPagesResponse)
def extract_pages(payload: ExtractPagesRequest):
    try:
        pages = []

        for url in payload.urls:
            result = extract_page_content(url)
            pages.append(ExtractedPage(**result))

        return ExtractPagesResponse(pages=pages)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка извлечения страниц: {str(e)}"
        )