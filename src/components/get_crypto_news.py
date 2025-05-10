import requests
import os
from dotenv import load_dotenv

load_dotenv()

serpapi_key = os.getenv('SERPAPI_KEY')

def get_crypto_news():
        """비트코인 관련 최신 뉴스 조회"""
        try:
            base_url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_news",
                "q": "bitcoin crypto trading",
                "api_key": serpapi_key,
                "gl": "us",
                "hl": "en"
            }
            
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                news_data = response.json()
                
                if 'news_results' not in news_data:
                    return None
                
                processed_news = []
                for news in news_data['news_results'][:5]: #상위 5개 뉴스만 처리
                    processed_news.append({
                        'title': news.get('title', ''),
                        'link': news.get('link', ''),
                        'source': news.get('source', {}).get('name', ''),
                        'date': news.get('data', ''),
                        'snippet': news.get('snippet', '')
                    })
                print("\n=== Latest Crypto News ===")
                for news in processed_news:
                    print(f"\nTitle: {news['title']}")
                    print(f"Source: {news['source']}")
                    print(f"Date: {news['date']}")
                    
                return processed_news
            return None
        except Exception as e:
            print(f"Error in get_crypto_news: {e}")
            return None