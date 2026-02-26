from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.prompts import Prompts
from config.config import Config

def generate_search_topics(question: str) -> list[str]:
    model = ChatOllama(
        model=Config.OLLAMA_MODEL,
        base_url=Config.OLLAMA_HOST,
        temperature=0.3
    )
    
    prompt = PromptTemplate.from_template(Prompts.SEARCH_TOPICS_SYSTEM_PROMPT)
    chain = prompt | model | StrOutputParser()
    raw_response = chain.invoke({
    "question": question, 
    "TOP_K": Config.TOP_K 
    })
    
    topics = [t.strip() for t in raw_response.split("|||") if t.strip()]
    
    if question not in topics:
        topics.insert(0, question)
        
    return topics[:Config.TOP_K]

def generate_final_answer(question: str, chunks: list) -> str:
    model = ChatOllama(
        model=Config.OLLAMA_MODEL,
        base_url=Config.OLLAMA_HOST,
        temperature=0.3 
    )
    
    context_text = ""
    for i, chunk in enumerate(chunks, 1):
        url = chunk.metadata.get("url", "Неизвестный источник")
        context_text += f"\nИсточник: {url} \n{chunk.page_content}\n"
        
    system_prompt = Prompts.FINAL_ANSWER_SYSTEM_PROMPT
    user_prompt_template = Prompts.FINAL_ANSWER_USER_PROMPT
    user_message_content = user_prompt_template.format(question=question, context=context_text)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message_content)
    ]
    
    print("\nМодель читает текст и пишет ответ")
    response = model.invoke(messages)
    answer = response.content
    
    unique_urls = set([chunk.metadata.get('url') for chunk in chunks if chunk.metadata.get('url')])
    if unique_urls:
        answer += "\n\nИспользованные источники:\n"
        for u in unique_urls:
            answer += f"- {u}\n"
            
    return answer
