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
import pandas as pd
import numpy as np

# Database và crawl functions
from Database.utils import init_database, get_news_table, save_news_table, delete_NewsID, get_history, save_history_table, get_ttp_table, save_ttp_table, generate_ttp_embeddings, map_ttp_from_text
from Database.search_engine import search_bm25, rerank_with_tfidf
from CrawlNews.crawl_vnexpress import crawl_vnexpress
from CrawlNews.crawl_congan import crawl_congan
from CrawlNews.crawl_dantri import crawl_dantri
from CrawlNews.crawl_thanhnien import crawl_thanhnien
from CrawlNews.crawl_nhandan import crawl_nhandan
from CrawlNews.crawl_cafef import crawl_cafef
from CrawlNews.crawl_antv import crawl_antv
from CrawlNews.crawl_vtv import crawl_vtv
from CrewAI.tools.search_googleapi import search_google_api
# Thêm thư mục CrewAI vào sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CrewAI'))
from CrewAI.pipeline import Pipeline

def initialize_database_and_crawl():
    init_database()
    sources = {
        "vnexpress": crawl_vnexpress,
        "congan": crawl_congan,
    }

    for name, crawl_func in sources.items():
        try:
            articles = crawl_func()
            for article in articles:
                if all(k in article for k in ['title', 'content', 'date', 'link']):
                    save_news_table(article['title'], article['content'], article['date'], article['link'])
            print(f"[✓] Crawled and saved articles from {name}")
        except Exception as e:
            print(f"[X] Error crawling {name}: {e}")

initialize_database_and_crawl()

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
        "name": "Management",
        "description": "Thêm hoặc xoá thông tin trong hệ thống",
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
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# ===================== MODELS =====================
class QueryRequest(BaseModel):
    query: str = ""

class News(BaseModel):
    title: str = ""
    content: str = ""
    link: str = ""
    date: str = ""

class TTPs(BaseModel):
    pattern: str = ""
    category: str = ""
    ttp: str = ""
    source: str = ""

class SourceNews(BaseModel):
    list_source: List[str]

# ===================== ROUTES =====================

@app.get("/", tags=["Info"])
async def read_root():
    return {"message": "Welcome to the FakeBuster System!"}

# === Management ===
@app.post("/add_news", tags=["Management"])
async def add_news(request: News):
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    date = datetime.now(vietnam_tz).strftime('%Y-%m-%d %H:%M:%S')
    save_news_table(request.title, request.content, date, request.link)
    return {"message": "News saved successfully!"}

@app.post("/add_ttps", tags=["Management"])
async def add_ttps(request: TTPs):
    save_ttp_table(request.pattern, request.category, request.ttp, request.source)
    return {"message": "TTP saved successfully!"}

@app.post("/add_ttps_form_file", tags=["Management"])
async def add_ttps_form_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    if not (filename.endswith(".csv") or filename.endswith(".xls") or filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="File phải là CSV hoặc Excel")

    try:
        if filename.endswith(".csv"):
            try:
                df = pd.read_csv(file.file, encoding='utf-8')
            except UnicodeDecodeError:
                file.file.seek(0)  # reset con trỏ file
                df = pd.read_csv(file.file, encoding='latin1') 
        else:
            df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi đọc file: {e}")

    df.columns = df.columns.str.strip().str.lower()

    for _, row in df.iterrows():
        save_ttp_table(
            pattern=str(row['pattern']),
            category=str(row['category']),
            ttp=str(row['ttp']),
            source=str(row['source']),
        )

    return {"message": f"Import thành công {len(df)} bản ghi"}

@app.post("/generate_ttp_embeddings", tags=["Management"])
async def api_generate_ttp_embeddings():
    try:
        generate_ttp_embeddings()
        return {"message": "Đã tạo và lưu FAISS index thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo FAISS index: {e}")

@app.delete("/delete_news", tags=["Management"])
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
        elif "cafef.vn" in url:
            articles = crawl_cafef()
        elif "antv.gov.vn" in url:
            articles = crawl_antv()
        elif "vtv.vn" in url:
            articles = crawl_vtv()
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

    ttp_matches = ''
    if "✅" not in result:
        ttp_matches = map_ttp_from_text(input_text)

    print('tìm thấy ttp_matches')

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
        "verification_result": result,
        "ttp_matches": ttp_matches
    }

# === Retrieval (RAG) ===
@app.get("/retrieval_news", tags=["Retrieval"])
async def retrieval_news(query: str):
    bm25_results = search_bm25(query)
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

@app.get("/get_news", tags=["Database"])
async def show_news():
    news_df = get_news_table()
    news_df['date'] = pd.to_datetime(news_df['date'], errors='coerce')
    news_df = news_df.sort_values(by='date', ascending=False)

    return {
        "total": len(news_df),
        "data": news_df.to_dict(orient="records")
    }

@app.get("/get_ttps", tags=["Database"])
async def get_ttps():
    ttp_df = get_ttp_table()
    return {
        "total": len(ttp_df),
        "data": ttp_df.to_dict(orient="records")
    }

@app.get("/get_history", tags=["Database"])
async def show_history():
    history_df = get_history()
    history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], errors='coerce')
    history_df = history_df.sort_values(by='timestamp', ascending=False)

    return {
        "total": len(history_df),
        "data": history_df.to_dict(orient="records")
    }

# ========== MAIN ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080)
