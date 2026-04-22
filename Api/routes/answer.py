from __future__ import annotations

from fastapi import APIRouter, HTTPException

from Api.schemas import (
    AnswerRequest,
    AnswerResponse,
    AnswerDebugResponse,
)

from search import get_search_engine
from llm import generate_search_topics, get_top_chunks, generate_final_answer
from Tools import filter_urls, filter_pages, rerank_chunks
from travily.travily import extract, save_used_pages


router = APIRouter(prefix="/api/answer", tags=["answer"])


def run_answer_pipeline(payload: AnswerRequest) -> dict:
    question = payload.question.strip()

    if not question:
        raise ValueError("Вопрос не может быть пустым.")

    search_engine = get_search_engine()

    print(f"\n[API] Вопрос: {question}")
    print(f"[API] Search engine: {search_engine.__class__.__name__}")

    print("\n[API] Генерация поисковых тем")
    topics = generate_search_topics(question)

    print("[API] Сгенерированные темы:")
    for i, topic in enumerate(topics, start=1):
        print(f"{i}. {topic}")

    print("\n[API] Поиск ссылок")
    urls_before_filter = search_engine.search(topics)
    print(f"[API] Найдено ссылок до фильтрации: {len(urls_before_filter)}")

    urls_after_filter = filter_urls(urls_before_filter)
    print(f"[API] Осталось ссылок после filter_urls: {len(urls_after_filter)}")

    urls_after_filter = urls_after_filter[:payload.max_results]

    if not urls_after_filter:
        return {
            "question": question,
            "generated_topics": topics,
            "found_urls_before_filter": urls_before_filter,
            "found_urls_after_filter": [],
            "pages": [],
            "top_chunks": [],
            "answer": "После фильтрации полезных ссылок не осталось.",
            "used_urls": [],
        }

    print("\n[API] Скачивание страниц")
    pages = extract(urls_after_filter, question=question)

    if not pages:
        return {
            "question": question,
            "generated_topics": topics,
            "found_urls_before_filter": urls_before_filter,
            "found_urls_after_filter": urls_after_filter,
            "pages": [],
            "top_chunks": [],
            "answer": "Не удалось скачать текст ни с одного сайта.",
            "used_urls": [],
        }

    print(f"[API] Страниц до filter_pages: {len(pages)}")
    pages = filter_pages(pages, question=question)
    print(f"[API] Осталось страниц после filter_pages: {len(pages)}")

    if not pages:
        return {
            "question": question,
            "generated_topics": topics,
            "found_urls_before_filter": urls_before_filter,
            "found_urls_after_filter": urls_after_filter,
            "pages": [],
            "top_chunks": [],
            "answer": "После фильтрации страниц полезного контента не осталось.",
            "used_urls": [],
        }

    print("\n[API] Получение релевантных чанков")
    top_chunks = get_top_chunks(pages, question)

    if not top_chunks:
        return {
            "question": question,
            "generated_topics": topics,
            "found_urls_before_filter": urls_before_filter,
            "found_urls_after_filter": urls_after_filter,
            "pages": pages,
            "top_chunks": [],
            "answer": "Не удалось получить релевантные чанки.",
            "used_urls": [],
        }

    print(f"[API] Чанков до rerank: {len(top_chunks)}")
    top_chunks = rerank_chunks(top_chunks, question)
    print(f"[API] Чанков после rerank: {len(top_chunks)}")

    print("\n[API] Генерация финального ответа")
    final_answer, used_urls = generate_final_answer(question, top_chunks)

    if payload.save_pages:
        try:
            save_used_pages(pages, used_urls)
        except Exception as e:
            print(f"[API] Ошибка save_used_pages: {e}")

    return {
        "question": question,
        "generated_topics": topics,
        "found_urls_before_filter": urls_before_filter,
        "found_urls_after_filter": urls_after_filter,
        "pages": pages,
        "top_chunks": top_chunks,
        "answer": final_answer,
        "used_urls": used_urls,
    }


@router.post("", response_model=AnswerResponse)
def answer_question(payload: AnswerRequest):
    try:
        result = run_answer_pipeline(payload)

        return AnswerResponse(
            answer=result["answer"],
            generated_topics=result["generated_topics"],
            found_urls=result["found_urls_after_filter"],
            used_urls=result["used_urls"],
            sources_count=len(result["pages"]),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации ответа: {str(e)}",
        )


@router.post("/debug", response_model=AnswerDebugResponse)
def answer_debug(payload: AnswerRequest):
    try:
        result = run_answer_pipeline(payload)

        return AnswerDebugResponse(
            question=result["question"],
            generated_topics=result["generated_topics"],
            found_urls_before_filter=result["found_urls_before_filter"],
            found_urls_after_filter=result["found_urls_after_filter"],
            pages_count=len(result["pages"]),
            chunks_count=len(result["top_chunks"]),
            used_urls=result["used_urls"],
            answer=result["answer"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка debug-ответа: {str(e)}",
        )