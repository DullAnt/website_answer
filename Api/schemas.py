from typing import List, Optional, Any
from pydantic import BaseModel, Field


class SearchLinksRequest(BaseModel):
    topics: List[str] = Field(..., description="Список поисковых запросов")
    max_results: int = Field(default=10, ge=1, le=100)


class SearchLinksResponse(BaseModel):
    urls: List[str]


class SearchRawRequest(BaseModel):
    query: str = Field(..., description="Один поисковый запрос")


class SearchRawResponse(BaseModel):
    query: str
    results: Any


class ExtractPagesRequest(BaseModel):
    urls: List[str] = Field(..., description="Список URL для извлечения текста")


class ExtractedPage(BaseModel):
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    success: bool
    error: Optional[str] = None


class ExtractPagesResponse(BaseModel):
    pages: List[ExtractedPage]


class AnswerRequest(BaseModel):
    question: str = Field(..., description="Вопрос пользователя")
    max_results: int = Field(default=5, ge=1, le=30)
    save_pages: bool = Field(default=True, description="Сохранять использованные страницы")


class AnswerResponse(BaseModel):
    answer: str
    generated_topics: List[str]
    found_urls: List[str]
    used_urls: List[str]
    sources_count: int


class AnswerDebugResponse(BaseModel):
    question: str
    generated_topics: List[str]
    found_urls_before_filter: List[str]
    found_urls_after_filter: List[str]
    pages_count: int
    chunks_count: int
    used_urls: List[str]
    answer: str