from llm.ollama import generate_search_topics, generate_final_answer
from travily.travily import search, extract
from llm.embeddings import get_top_chunks
from Tools import filter_urls, filter_pages, rerank_chunks

def main():
    question = input("Введите ваш вопрос или 'q' для выхода: ").strip()
    if question.lower() == "q":
        return

    print(f"\nВаш вопрос: {question}")

    while True:
        print("\nГенерация подтем")
        topics = generate_search_topics(question)

        print("\nСгенерированные темы:")
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic}")

        approval = input("\nВы одобряете эти темы для поиска? (y - да, n - ввести свои): ").strip().lower()
        if approval != "y":
            custom_topics = input("Введите ваши темы через запятую: ").strip()
            topics = [t.strip() for t in custom_topics.split(",") if t.strip()]

        print("\nИщем ссылки через Tavily")
        urls = search(topics)
        print(f"Найдено ссылок: {len(urls)}")

        urls = filter_urls(urls)
        print(f"Осталось ссылок после filter_urls: {len(urls)}")

        if not urls:
            print("Ссылки не найдены.")
            continue

        print("\nСкачиваем данные")
        pages = extract(urls, question=question)

        if not pages:
            print("Не удалось скачать текст ни с одного сайта.")
            continue

        print(f"Страниц до filter_pages: {len(pages)}")
        pages = filter_pages(pages, question)
        print(f"Осталось страниц после filter_pages: {len(pages)}")

        if not pages:
            print("После фильтрации страниц полезного контента не осталось.")
            continue

        print("\nОбработка текста")
        top_chunks = get_top_chunks(pages, question)

        if not top_chunks:
            print("Не удалось получить релевантные чанки.")
            continue
        
        print(f"Чанков до rerank: {len(top_chunks)}")
        top_chunks = rerank_chunks(top_chunks, question)
        print(f"Чанков после rerank: {len(top_chunks)}")


        print("\nСсылки, по которым собран текст:")
        shown = set()
        for page in pages:
            url = page.get("url")
            if url and url not in shown:
                shown.add(url)
                print(f" -> {url}")

        proceed = input("\nОдобряете ли вы эти ссылки для генерации финального ответа? (y - продолжить, n - искать заново): ").strip().lower()

        if proceed == "y":
            print("\nНачинаем генерацию")
            break
        else:
            print("\nДавайте уточним запрос и попробуем найти другие источники.")
            new_q = input(f"Можете уточнить вопрос (нажмите Enter, чтобы оставить '{question}'): ").strip()
            if new_q:
                question = new_q

    final_answer = generate_final_answer(question, top_chunks)
    print("\n" + final_answer)


if __name__ == "__main__":
    main()