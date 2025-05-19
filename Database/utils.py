import os
import pandas as pd
from sqlalchemy import create_engine
import random
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np

# Load biến môi trường
load_dotenv()

# Lấy DB path từ .env
DB_PATH = os.getenv("DB_PATH", "news_database.db")
VECTORDB_PATH = os.getenv("VECTORDB_PATH", "faiss_ttp.index")
engine = create_engine(f"sqlite:///{DB_PATH}")

def init_database():
    news_df = pd.DataFrame(columns=["id", "title", "content", "date", "source"])
    news_df.to_sql('news_table', con=engine, if_exists='replace', index=False)

    ttp_df = pd.DataFrame(columns=["pattern", "category", "ttp", "source"]) 
    ttp_df.to_sql('ttp_table', con=engine, if_exists='replace', index=False)

    history_df = pd.DataFrame(columns=["id", "request", "response", "timestamp"])
    history_df.to_sql('history_table', con=engine, if_exists='replace', index=False)

def get_news_table():
    return pd.read_sql_table('news_table', engine)

def delete_NewsID(id):
    news_df = pd.read_sql_table('news_table', engine)

    if id not in news_df["id"].values:
        return {"error": "Mail ID không tồn tại"}

    news_df = news_df[news_df["id"] != id]
    news_df.to_sql('news_table', con=engine, if_exists='replace', index=False)

    return {"message": f"Tin tức với ID: {id} đã được xóa"}

def generate_unique_id():
    existing_ids = set(pd.read_sql_table('news_table', con=engine)['id'])

    while True:
        new_id = f"ID{random.randint(10000000, 99999999)}"
        if new_id not in existing_ids:
            return new_id

def save_news_table(title, content, date, source):
    existing_data = pd.read_sql_table('news_table', engine)
    if title in existing_data["title"].values:
        return  # Nếu tồn tại, bỏ qua

    new_id = generate_unique_id()
    news_df = pd.DataFrame([{
        "id": new_id,
        "title": title,
        "content": content,
        "date": date,
        "source": source
    }])

    news_df.to_sql('news_table', con=engine, if_exists='append', index=False)

def save_ttp_table(pattern, category, ttp, source):
    existing_data = pd.read_sql_table('ttp_table', engine)
    if pattern in existing_data["pattern"].values:
        return  

    if category in existing_data["category"].values:
        return  
    
    ttp_df = pd.DataFrame([{
        "pattern": pattern,
        "category": category,
        "ttp": ttp,
        "source": source
    }])
    with engine.begin() as conn:
        ttp_df.to_sql('ttp_table', con=conn, if_exists='append', index=False)

def save_history_table(id, request, response, date):
    history_df = pd.DataFrame([{
        "id": id,
        "request": request,
        "response": response,
        "timestamp": date,
    }])
    history_df.to_sql('history_table', con=engine, if_exists='append', index=False)

def get_history():
    return pd.read_sql_table('history_table', engine)

def get_ttp_table():
    return pd.read_sql_table('ttp_table', engine)

def generate_ttp_embeddings(output_path=VECTORDB_PATH):
    # Load dữ liệu TTP từ DB
    ttp_df = pd.read_sql_table('ttp_table', engine)
    if ttp_df.empty:
        print("Bảng ttp_table đang rỗng, không tạo được embeddings.")
        return

    # Chuẩn bị văn bản embedding: kết hợp pattern và category
    texts = (ttp_df["pattern"].astype(str) + " - " + ttp_df["category"].astype(str)).tolist()

    # Khởi tạo model embedding
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = model.encode(texts, normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(np.array(embeddings).astype("float32"))

    # Tạo folder nếu cần
    dir_path = os.path.dirname(output_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    faiss.write_index(index, output_path)
    print(f"FAISS index lưu tại: {output_path}")

def map_ttp_from_text(text, top_k=2, threshold=0.4):
    # Đảm bảo file index tồn tại
    if not os.path.exists(VECTORDB_PATH):
        raise FileNotFoundError("Chưa có file FAISS index. Vui lòng chạy generate_ttp_embeddings trước.")

    # Load FAISS index
    index = faiss.read_index(VECTORDB_PATH)

    # Load patterns từ DB
    ttp_df = pd.read_sql_table('ttp_table', engine)
    if ttp_df.empty:
        print("Bảng ttp_table rỗng, không thể map TTP")
        return []

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    input_emb = model.encode([text], normalize_embeddings=True).astype("float32")

    D, I = index.search(input_emb, top_k)

    results = []
    for score, idx in zip(D[0], I[0]):
        if score >= threshold and idx < len(ttp_df):
            row = ttp_df.iloc[idx]
            results.append({
                "category": row["category"],
                "ttp": row["ttp"],
                "source": row["source"],
                "similarity": round(float(score), 3)
            })
    return results