from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Api.routes.health import router as health_router
from Api.routes.search import router as search_router
from Api.routes.extract import router as extract_router
from Api.routes.answer import router as answer_router


app = FastAPI(
    title="Website Answer API",
    version="1.0.0",
    description="API для поиска ссылок через SearXNG, извлечения текста со страниц и генерации ответов."
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для разработки нормально, для продакшена лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Website Answer API",
        "docs": "/docs",
        "health": "/api/health"
    }


app.include_router(health_router)
app.include_router(search_router)
app.include_router(extract_router)
app.include_router(answer_router)