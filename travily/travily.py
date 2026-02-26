from tavily import TavilyClient
from config.config import Config

tavily_client = TavilyClient(api_key=Config.TRAVILY_API)

def search(topics: list[str]) -> list[str]:
    unique_urls = set()
    
    for topic in topics:
        try:
            response = tavily_client.search(topic, max_results=Config.TOP_K)
            for result in response.get('results', []):
                unique_urls.add(result['url'])
        except Exception as e:
            print(f"Ошибка при поиске '{topic}': {e}")
            
    return list(unique_urls)

def extract(urls: list[str]) -> list[dict]:
    extracted_data = []
    
    try:
        response = tavily_client.extract(urls)
        for result in response.get('results', []):
            extracted_data.append({
                "url": result.get('url'),
                "content": result.get('raw_content', '')
            })
    except Exception as e:
        print(f"Ошибка при извлечении контента: {e}")
        
    return extracted_data
