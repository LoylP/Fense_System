from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pytz
from datetime import datetime
import sys
import os
import shutil
import random
import json
import numpy as np
from sqlalchemy import create_engine

# Database và crawl functions
from Database.utils import init_database, get_ds_scamcheck, get_news_table, save_news_table, delete_NewsID, get_history, save_history_table
from Database.search_engine import search_bm25, rerank_with_tfidf
from CrawlNews.crawl_vnexpress import crawl_vnexpress
from CrawlNews.crawl_congan import crawl_congan
from CrawlNews.crawl_dantri import crawl_dantri
from CrawlNews.crawl_thanhnien import crawl_thanhnien
from CrawlNews.crawl_nhandan import crawl_nhandan
from CrewAI.tools.search_googleapi import search_google_api
# Thêm thư mục CrewAI vào sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CrewAI'))
from CrewAI.pipeline import Pipeline

# 🏷️ Khai báo metadata cho Swagger
tags_metadata = [
    {
        "name": "Crawl",
        "description": "API thu thập dữ liệu báo từ các nguồn báo điện tử",
    },
    {
        "name": "Requests",
        "description": "Các API cho phép người dùng gửi yêu cầu xác thực",
    },
    {
        "name": "Retrieval",
        "description": "Các API dùng để tìm kiếm tin tức (RAG, BM25, TF-IDF, Google Search)",
    },
    {
        "name": "Database",
        "description": "Truy xuất dữ liệu trong hệ thống từ bảng lịch sử, tin tức, scamcheck...",
    },
    {
        "name": "News Management",
        "description": "Thêm hoặc xoá bài báo trong hệ thống",
    }
]

app = FastAPI(
    title="FENSE API",
    description="Hệ thống kiểm chứng và truy xuất tin giả trên nhiều nền tảng.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

DB_PATH = '/home/phuc/project/FakeBuster_System/news_database.db'
engine = create_engine(f"sqlite:///{DB_PATH}")

# ===================== MODELS =====================
class QueryRequest(BaseModel):
    query: str = ""

class News(BaseModel):
    title: str = ""
    content: str = ""
    link: str = ""
    date: str = ""

class SourceNews(BaseModel):
    list_source: List[str]

# ===================== ROUTES =====================

@app.get("/", tags=["Info"])
async def read_root():
    return {"message": "Welcome to the FakeBuster System!"}

# === News Management ===
@app.post("/add_news", tags=["News Management"])
async def add_news(request: News):
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    date = datetime.now(vietnam_tz).strftime('%Y-%m-%d %H:%M:%S')
    save_news_table(request.title, request.content, date, request.link)
    return {"message": "News saved successfully!"}

@app.delete("/delete_news", tags=["News Management"])
async def delete_news(id: str):
    delete_NewsID(id)
    return {"message": "News deleted successfully!"}

# === Crawl ===
@app.post("/pipeline_crawl_news", tags=["Crawl"])
async def pipeline_crawl_news(source_news: SourceNews):
    list_source = source_news.list_source
    total_saved = 0

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
            continue

        for article in articles:
            save_news_table(article['title'], article['content'], article['date'], article['link'])
            total_saved += 1

    return {"message": f"Đã lưu thành công {total_saved} bài báo vào database!"}

@app.post("/verify_input", tags=["Requests"])
async def verify_input(
    input_text: Optional[str] = Form(None),
    input_image: Optional[UploadFile] = File(None)
):
    if not input_text and not input_image:
        return {"message": "Bạn cần gửi lên input dạng văn bản hoặc ảnh."}

    image_path = None
    if input_image:
        image_path = os.path.join(TEMP_DIR, input_image.filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(input_image.file, f)

    # Gọi Pipeline để xử lý
    verifier = Pipeline(text_input=input_text, image_path=image_path)
    result = verifier.run()

    # Gộp request input
    request_str = input_text or ""
    if input_image:
        request_str += f" [IMAGE: {input_image.filename}]"

    # Tạo ID và thời gian
    id = random.randint(0, 99999)
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    date = datetime.now(vietnam_tz).strftime('%Y-%m-%d %H:%M:%S')

    #Lưu lịch sử
    save_history_table(
        id=id,
        request=request_str,
        response=result.raw if hasattr(result, "raw") else str(result),
        date=date
    )

    return {
        "message": "Phân tích và xác minh hoàn tất!",
        "input_text": input_text,
        "input_image": input_image.filename if input_image else None,
        "verification_result": result
    }

# === Retrieval (RAG) ===
@app.get("/retrieval_news", tags=["Retrieval"])
async def retrieval_news(query: str):
    bm25_results = search_bm25(query, engine)
    final_results = rerank_with_tfidf(bm25_results, query)

    for result in final_results:
        for key, value in result.items():
            if isinstance(value, np.integer):
                result[key] = int(value)

    return {"results": final_results}

@app.get("/search", tags=["Retrieval"])
async def search(query: str):
    try:
        news_df = search_google_api(query)
        if news_df.empty:
            raise HTTPException(status_code=404, detail="No valid search results found.")
        return news_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Database Access ===
@app.get("/get_danhsach_scamcheck", tags=["Database"])
async def show_ds():
    scamcheck_df = get_ds_scamcheck()
    return {
        "total": len(scamcheck_df),
        "data": scamcheck_df.to_dict(orient="records")
    }

@app.get("/get_news", tags=["Database"])
async def show_news():
    news_df = get_news_table()
    return {
        "total": len(news_df),
        "data": news_df.to_dict(orient="records")
    }

@app.get("/get_history", tags=["Database"])
async def show_history():
    history_df = get_history()
    return {
        "total": len(history_df),
        "data": history_df.to_dict(orient="records")
    }

# ========== MAIN ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
