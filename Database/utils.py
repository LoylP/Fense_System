import os
import pandas as pd
from sqlalchemy import create_engine
import random
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Lấy DB path từ .env
DB_PATH = os.getenv("DB_PATH", "news_database.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

def init_database():
    news_df = pd.DataFrame(columns=["id", "title", "content", "date", "source"])
    news_df.to_sql('news_table', con=engine, if_exists='replace', index=False)

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
