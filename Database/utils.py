import pandas as pd
from sqlalchemy import create_engine
import random

def init_database():
    engine = create_engine('sqlite:///news_database.db')
    df = pd.read_csv('/home/phuc/Dev/FakeBuster_System/Database/scam_data.csv')
    df.to_sql('scamcheck_table', con=engine, if_exists='replace', index=False)

    news_df = pd.DataFrame(columns=["id", "title", "content", "date", "source"]) 
    news_df.to_sql('news_table', con=engine, if_exists='replace', index=False)

    history_df = pd.DataFrame(columns=["id", "request", "response", "timestamp"]) 
    history_df.to_sql('history_table', con=engine, if_exists='replace', index=False)

    return df

def get_ds_scamcheck():
    engine = create_engine('sqlite:///news_database.db')
    return pd.read_sql_table('scamcheck_table', engine)

def add_data_to_database(path_data):
    engine = create_engine('sqlite:///news_database.db')
    df_new = pd.read_csv(path_data)

    # Thêm dữ liệu vào bảng, đảm bảo không trùng lặp
    existing_data = pd.read_sql_table('scamcheck_table', engine)
    combined_data = pd.concat([existing_data, df_new]).drop_duplicates()

    combined_data.to_sql('scamcheck_table', con=engine, if_exists='replace', index=False)

def get_news_table():
    engine = create_engine('sqlite:///news_database.db')
    return pd.read_sql_table('news_table', engine)

def delete_NewsID(id):
    engine = create_engine('sqlite:///news_database.db')
    news_df = pd.read_sql_table('news_table', engine)
    
    if id not in news_df["id"].values:
        return {"error": "Mail ID không tồn tại"}

    news_df = news_df[news_df["id"] != id]
    news_df.to_sql('news_table', con=engine, if_exists='replace', index=False)

    return {"message": f"Tin tức với ID: {id} đã được xóa"}

def generate_unique_id(engine):
    """Tạo ID theo định dạng 'CAxxxxx' và kiểm tra trùng lặp."""
    existing_ids = set(pd.read_sql_table('news_table', con=engine)['id'])

    while True:
        new_id = f"ID{random.randint(10000000, 99999999)}"
        if new_id not in existing_ids:
            return new_id
        
def save_news_table(title, content, date, source):
    engine = create_engine('sqlite:///news_database.db')

    # Tạo ID ngẫu nhiên theo định dạng "IDxxxxxxxx"
    new_id = generate_unique_id(engine)

    # Tạo DataFrame mới
    news_df = pd.DataFrame([{
        "id": new_id,
        "title": title,
        "content": content,  
        "date": date,
        "source": source
    }])

    # Ghi vào database
    news_df.to_sql('news_table', con=engine, if_exists='append', index=False)

def save_history_table(id, request, response, date):
    engine = create_engine('sqlite:///news_database.db')

    # Tạo DataFrame mới
    history_df = pd.DataFrame([{
        "id": id,
        "request": request,
        "response": response,
        "timestamp": date, 
    }])

    # Ghi vào database
    history_df.to_sql('history_table', con=engine, if_exists='append', index=False)

def get_history():
    engine = create_engine('sqlite:///news_database.db')
    return pd.read_sql_table('history_table', engine)

# init_database()