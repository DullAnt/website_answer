import re
from collections import OrderedDict
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage

from prompts.prompts import Prompts
from config.config import Config


def _build_model() -> ChatOllama:
    return ChatOllama(
        model=Config.OLLAMA_MODEL,
        base_url=Config.OLLAMA_HOST,
        temperature=0.3,
        num_predict=2048,
    )


def _build_context_text(chunks: list) -> str:
    context_parts = []

    for chunk in chunks:
        url = chunk.metadata.get("url", "Неизвестный источник")
        rank = chunk.metadata.get("rank_in_url")
        chunk_index = chunk.metadata.get("chunk_index")

        context_parts.append(
            f"Источник: {url}\n"
            f"chunk_index: {chunk_index}\n"
            f"rank_in_url: {rank}\n"
            f"{chunk.page_content}\n"
        )

    return "\n".join(context_parts)


def _group_chunks_by_url(chunks: list) -> list[tuple[str, list]]:
    grouped = OrderedDict()

    for chunk in chunks:
        url = chunk.metadata.get("url")
        if not url:
            continue
        grouped.setdefault(url, []).append(chunk)

    return list(grouped.items())

def _extract_used_urls_from_answer(answer: str, chunks: list) -> list[str]:
    if not answer:
        return []

    candidate_urls = []
    seen = set()

    for chunk in chunks:
        url = chunk.metadata.get("url")
        if url and url not in seen:
            seen.add(url)
            candidate_urls.append(url)

    answer_lower = answer.lower()
    used_urls = []

    for url in candidate_urls:
        if url.lower() in answer_lower:
            used_urls.append(url)

    return used_urls

def _iter_batches(items: list, batch_size: int):
    batch_size = max(1, batch_size)
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def generate_search_topics(question: str, topics_count: int = 5) -> list[str]:
    model = _build_model()

    prompt = PromptTemplate.from_template(Prompts.SEARCH_TOPICS_SYSTEM_PROMPT)
    chain = prompt | model | StrOutputParser()

    raw_response = chain.invoke({
        "question": question,
        "TOP_K": Config.TOP_K,
    })

    topics = [t.strip() for t in raw_response.split("|||") if t.strip()]

    if question not in topics:
        topics.insert(0, question)

    return topics[:Config.TOP_K]


def select_relevant_links(
    question: str,
    page_text: str,
    candidate_links: list[str],
    limit: int = 2,
) -> list[str]:
    if not candidate_links:
        return []

    model = _build_model()
    page_excerpt = (page_text or "")[:2500]
    links_as_text = "\n".join(candidate_links[:30])

    prompt = PromptTemplate.from_template(Prompts.LINK_SELECTION_PROMPT)
    chain = prompt | model | StrOutputParser()

    raw_response = chain.invoke({
        "question": question,
        "page_excerpt": page_excerpt,
        "candidate_links": links_as_text,
        "limit": limit,
    })

    selected = [u.strip() for u in raw_response.split("|||") if u.strip()]
    selected = [u for u in selected if u in candidate_links]

    if not selected:
        return candidate_links[:limit]

    return selected[:limit]


def _generate_answer_from_context(question: str, context_text: str) -> str:
    model = _build_model()

    system_prompt = Prompts.FINAL_ANSWER_SYSTEM_PROMPT
    user_prompt_template = Prompts.FINAL_ANSWER_USER_PROMPT
    user_message_content = user_prompt_template.format(
        question=question,
        context=context_text,
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message_content),
    ]

    response = model.invoke(messages)
    return str(response.content).strip()


def _refine_answer(question: str, previous_answer: str, context_text: str) -> str:
    model = _build_model()

    messages = [
        SystemMessage(content=Prompts.FINAL_ANSWER_SYSTEM_PROMPT),
        HumanMessage(
            content=Prompts.FINAL_ANSWER_USER_PROMPT.format(
                question=question,
                previous_answer=previous_answer,
                context=context_text,
            )
        ),
    ]

    response = model.invoke(messages)
    return str(response.content).strip()


def generate_final_answer(question: str, chunks: list) -> str:
    if not chunks:
        return "К сожалению, я не нашел точного ответа на этот вопрос в найденных источниках."

    grouped_by_url = _group_chunks_by_url(chunks)

    if not grouped_by_url:
        return "К сожалению, я не нашел точного ответа на этот вопрос в найденных источниках."

    batches = list(_iter_batches(grouped_by_url, Config.BATCH_URL))

    accumulated_answer = ""

    for batch_index, batch in enumerate(batches, start=1):
        batch_chunks = []
        for _, url_chunks in batch:
            batch_chunks.extend(url_chunks)

        context_text = _build_context_text(batch_chunks)

        print(f"\nОбработка батча {batch_index}/{len(batches)}")
        print(f"URL в батче: {len(batch)}")

        if not accumulated_answer:
            accumulated_answer = _generate_answer_from_context(question, context_text)
        else:
            accumulated_answer = _refine_answer(question, accumulated_answer, context_text)

        used_urls = _extract_used_urls_from_answer(accumulated_answer, chunks)

        if used_urls:
            accumulated_answer += "\n\nИспользованные источники:\n"
        for u in used_urls:
            accumulated_answer += f"- {u}\n"

        return accumulated_answer, used_urls