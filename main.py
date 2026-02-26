import os
from llm.ollama import generate_search_topics, generate_final_answer
from travily.travily import search, extract
from llm.embeddings import get_top_chunks 

def main():
    question = input("Введите ваш вопрос или 'q' для выхода: ")
    if question.lower() == 'q': 
        return

    print(f"\nВаш вопрос: {question}")
    
    while True:
        print("\nГенерация подтем")
        topics = generate_search_topics(question)
        
        print("\nСгенерированные темы:")
        for i, t in enumerate(topics, 1):
            print(f" {i}. {t}")
            
        approval = input("\nВы одобряете эти темы для поиска? (y - да, n - ввести свои): ").strip().lower()
        if approval != 'y':
            custom_topics = input("Введите ваши темы через запятую: ")
            topics = [t.strip() for t in custom_topics.split(",")]

        print("\nИщем ссылки через Tavily")
        urls = search(topics)
        print(f"Найдено ссылок: {len(urls)}.")
        
        if not urls:
            print("Cсылки не найдены.")
            continue 
            
        print("Скачиваем данные")
        pages = extract(urls)
        if not pages:
            print("Не удалось скачать текст ни с одного сайта.")
            continue
            
        print("\nОбработка текста")
        top_chunks = get_top_chunks(pages, question)
        
        relevant_urls = urls
        
        print("Ссылки найденные на сайтах:")
        for u in relevant_urls:
            print(f" -> {u}")
        
        proceed = input("Одобряете ли вы эти ссылки для генерации финального ответа? (y - продолжить, n - искать заново): ").strip().lower()
        
        if proceed == 'y':
            print("\nНачинаем генерацию")
            break
        else:
            print("\nДавайте уточним запрос и попробуем найти другие источники.")
            new_q = input(f"Можете уточнить вопрос (нажмите Enter, чтобы оставить '{question}'): ").strip()
            if new_q:
                question = new_q

    final_answer = generate_final_answer(question, top_chunks)
    
    print(final_answer)

if __name__ == "__main__":
    main()
