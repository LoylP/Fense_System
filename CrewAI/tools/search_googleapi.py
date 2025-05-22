import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

def google_search(query, api_key, cse_id, num=10):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num).execute()
    return res.get('items', [])

def fetch_page_content(url, timeout=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else 'No title'
        body = ' '.join(p.get_text().strip() for p in soup.find_all('p'))
        return title, body[:1000]  # chỉ lấy 1000 ký tự đầu tiên để tối ưu
    except requests.RequestException as e:
        return None, None

def search_google_api(query, max_results=5):
    api_key = os.getenv("API_GOOGLE_CREDENTIAL")
    cse_id = os.getenv("SEARCH_ENGINE_CSE_ID")
    if not api_key or not cse_id:
        raise ValueError("🔑 API key hoặc Search Engine ID bị thiếu trong môi trường")

    try:
        search_results = google_search(query, api_key, cse_id, num=10)
    except Exception as e:
        print(f"❌ Lỗi gọi Google Custom Search API: {e}")
        # Trả về DataFrame rỗng hoặc có thể trả về lỗi dạng dict hoặc None tùy ý bạn
        return pd.DataFrame()

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {
            executor.submit(fetch_page_content, result['link']): result['link']
            for result in search_results
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title, content = future.result()
                if title and content:
                    results.append({
                        "url": url,
                        "title": title,
                        "content": content
                    })
                    if len(results) >= max_results:
                        break
            except Exception as e:
                print(f"⚠️ Lỗi xử lý URL: {url} | {e}")

    news_df = pd.DataFrame(results)
    return news_df

if __name__ == "__main__":
    api_key = os.getenv("API_GOOGLE_CREDENTIAL")
    cse_id = os.getenv("SEARCH_ENGINE_CSE_ID")

    print(api_key)
    print(cse_id)