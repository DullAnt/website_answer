import re
from typing import List, Any


def _question_keywords(question: str) -> set[str]:
    return {
        word.lower()
        for word in re.findall(r"\w+", question)
        if len(word) >= 3
    }


def _keyword_bonus(text: str, keywords: set[str]) -> int:
    lowered = text.lower()
    return sum(1 for word in keywords if word in lowered)


def rerank_chunks(chunks: List[Any], question: str) -> List[Any]:
    keywords = _question_keywords(question)

    def sort_key(chunk):
        base_score = float(chunk.metadata.get("score", 9999.0))
        text = chunk.page_content or ""
        bonus = _keyword_bonus(text, keywords)

        url = str(chunk.metadata.get("url", "")).lower()
        url_bonus = 0
        for marker in ["build", "guide", "class", "tips", "best", "beginner", "walkthrough"]:
            if marker in url:
                url_bonus += 1

        # меньше score = лучше
        # больше bonus = лучше
        return (base_score, -(bonus + url_bonus))

    reranked = sorted(chunks, key=sort_key)

    print("[rerank_chunks] чанки пересортированы")
    for i, chunk in enumerate(reranked[:10], start=1):
        print(
            f"  {i}. score={chunk.metadata.get('score')} | "
            f"url={chunk.metadata.get('url')} | "
            f"chunk_index={chunk.metadata.get('chunk_index')}"
        )

    return reranked