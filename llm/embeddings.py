import os
import faiss
import hashlib
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document

from config.config import Config


def _make_content_hash(url: str, content: str) -> str:
    raw = f"{url}\n{content}".encode("utf-8", errors="ignore")
    return hashlib.md5(raw).hexdigest()


def _load_or_create_vectorstore(embeddings):
    faiss_dir = Config.FAISS_DB_DIR

    if os.path.exists(faiss_dir):
        try:
            print(f"Загрузка существующего FAISS из: {faiss_dir}")
            return FAISS.load_local(
                folder_path=faiss_dir,
                embeddings=embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            print(f"Не удалось загрузить существующий FAISS: {e}")
            print("Создаём новый пустой индекс.")

    index = faiss.IndexFlatL2(len(embeddings.embed_query("questions")))
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    return vector_store


def _get_existing_hashes(vectorstore) -> set[str]:
    existing_hashes = set()

    try:
        store_dict = getattr(vectorstore.docstore, "_dict", {})
        for doc in store_dict.values():
            if isinstance(doc, Document):
                content_hash = doc.metadata.get("content_hash")
                if content_hash:
                    existing_hashes.add(content_hash)
    except Exception as e:
        print(f"Не удалось прочитать существующие hashes из FAISS: {e}")

    return existing_hashes


def get_top_chunks(pages: list[dict], question: str) -> list[Document]:
    docs = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    for page in pages:
        url = page.get("url")
        content = (page.get("content") or "").strip()

        if not url or not content:
            continue

        if len(content) < 1200:
            content_hash = _make_content_hash(url, content)
            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "url": url,
                        "chunk_index": 0,
                        "content_hash": content_hash,
                    }
                )
            )
        else:
            chunks = text_splitter.split_text(content)
            for idx, chunk in enumerate(chunks):
                chunk = chunk.strip()
                if not chunk:
                    continue

                content_hash = _make_content_hash(url, chunk)
                docs.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "url": url,
                            "chunk_index": idx,
                            "content_hash": content_hash,
                        }
                    )
                )

    print(f"Текст разбит на {len(docs)} чанков.")

    if not docs:
        print("Нет документов для индексации.")
        return []

    print(f"Загружаем модель эмбеддингов: {Config.EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={"device": Config.DEVICE}
    )

    vectorstore = _load_or_create_vectorstore(embeddings)

    existing_hashes = _get_existing_hashes(vectorstore)
    docs_to_add = []
    seen_in_batch = set()

    for doc in docs:
        content_hash = doc.metadata.get("content_hash")

        if not content_hash:
            docs_to_add.append(doc)
            continue

        if content_hash in existing_hashes:
            continue

        if content_hash in seen_in_batch:
            continue

        seen_in_batch.add(content_hash)
        docs_to_add.append(doc)

    print(f"Новых чанков для добавления: {len(docs_to_add)}")

    if docs_to_add:
        uuids = [str(uuid4()) for _ in range(len(docs_to_add))]
        vectorstore.add_documents(documents=docs_to_add, ids=uuids)

        print("Сохранение в БД")
        os.makedirs(Config.FAISS_DB_DIR, exist_ok=True)
        vectorstore.save_local(Config.FAISS_DB_DIR)
    else:
        print("Новых чанков нет, индекс не обновлялся.")

    ordered_urls = []
    seen_urls = set()

    for page in pages:
        url = page.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            ordered_urls.append(url)

    top_chunks = []

    print(f"Ищем top {Config.TOP_K} чанков для каждого URL")

    for url in ordered_urls:
        try:
            results = vectorstore.similarity_search_with_score(
                question,
                k=Config.TOP_K,
                filter={"url": url}
            )

            print(f"\nURL: {url}")
            print(f"Найдено чанков: {len(results)}")

            for rank, (doc, score) in enumerate(results, start=1):
                doc_with_score = Document(
                    page_content=doc.page_content,
                    metadata={
                        **doc.metadata,
                        "score": float(score),
                        "rank_in_url": rank,
                    }
                )
                top_chunks.append(doc_with_score)

                print(
                    f"  {rank}. score={score:.4f} | "
                    f"chunk_index={doc.metadata.get('chunk_index')}"
                )

        except Exception as e:
            print(f"Ошибка при поиске чанков для URL '{url}': {e}")

    return top_chunks