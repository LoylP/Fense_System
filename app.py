from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Database.utils import init_database, get_ds_scamcheck, get_news_table, save_news_table, delete_NewsID, get_history
from Database.search_engine import search_bm25, rerank_with_tfidf
from CrawlNews.crawl_vnexpress import crawl_vnexpress
from CrawlNews.crawl_congan import crawl_congan
from CrawlNews.crawl_dantri import crawl_dantri
from CrawlNews.crawl_thanhnien import crawl_thanhnien
from CrawlNews.crawl_nhandan import crawl_nhandan
from Utils.search_googleapi import search_google_api
import pytz
from typing import Optional, List
from datetime import datetime
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# print("Initializing database...")
# init_database()

class QueryRequest(BaseModel):
    query: str = ""

class News(BaseModel):
    title: str = ""
    content: str = ""
    link: str = ""
    date: str = ""

class SourceNews(BaseModel):
    list_source: List[str]

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FakeBuster System!"}

@app.post("/add_news")
async def add_news(request: News):
    # Lấy thời gian hiện tại theo múi giờ Việt Nam
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    date = datetime.now(vietnam_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Lưu vào database
    save_news_table(request.title, request.content, date, request.source)

    return {"message": "News saved successfully!"}

@app.post("/pipeline_crawl_news")
async def pipeline_crawl_news(source_news: SourceNews):
    """
    API nhận danh sách nguồn tin từ người dùng, xác định nguồn tự động và tiến hành crawl dữ liệu.
    """
    list_source = source_news.list_source
    total_saved = 0

    # Lặp qua từng link để xác định nguồn
    for url in list_source:
        if "dantri.com.vn" in url:
            articles = crawl_dantri()
        elif "vnexpress.net" in url:
            articles = crawl_vnexpress()
        elif "congan.com.vn" in url:
            articles = crawl_congan()
        elif "nhandan.vn" in url:
            articles = crawl_nhandan()
        elif "thanhnien.vn" in url:
            articles = crawl_thanhnien()
        else:
            continue  # Bỏ qua nếu không xác định được nguồn

        # Lưu dữ liệu vào database
        for article in articles:
            save_news_table(article['title'], article['content'], article['date'], article['link'])
            total_saved += 1

    return {"message": f"Đã lưu thành công {total_saved} bài báo vào database!"}

@app.get("/retrieval_news")
async def retrieval_news(query: str):
    bm25_results = search_bm25(query)
    final_results = rerank_with_tfidf(bm25_results, query)

    for result in final_results:
        for key, value in result.items():
            if isinstance(value, np.integer):
                result[key] = int(value)

    return {"results": final_results}

@app.get("/search")
async def search(query: str):
    try:
        news_df = search_google_api(query)
        if news_df.empty:
            raise HTTPException(status_code=404, detail="No valid search results found.")
        return news_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get_danhsach_scamcheck")
async def show_ds():
    scamcheck_df = get_ds_scamcheck()
    return scamcheck_df.to_dict(orient="records")

@app.get("/get_news")
async def show_news():
    news_df = get_news_table()
    return news_df.to_dict(orient="records")

@app.get("/get_history")
async def show_history():
    history_df = get_history()
    return history_df.to_dict(orient="records")

@app.delete("/delete_news")
async def delete_news(id: str):
    delete_NewsID(id)
    return {"message": "Mail deleted successfully!"}

if __name__== "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)