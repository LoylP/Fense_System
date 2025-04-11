import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from rank_bm25 import BM25Okapi
import re
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
engine = create_engine(f"sqlite:///{DB_PATH}")

def clean_text(text):
    """Chuẩn hóa văn bản"""
    return re.sub(r"[^\w\s]", "", text).strip().lower() if isinstance(text, str) else ""

def simple_tokenize(text):
    """Tokenize đơn giản bằng regex"""
    return re.findall(r'\b\w+\b', text.lower())

def load_data_from_db():
    """Tải dữ liệu từ database"""
    df = pd.read_sql_table('news_table', con=engine).fillna('')
    df['clean_content'] = df['content'].apply(clean_text)
    df['clean_title'] = df['title'].apply(clean_text)
    return df

def build_bm25_index(df):
    """Tạo chỉ mục BM25 từ dữ liệu đã xử lý"""
    combined = df['clean_content'] + " " + df['clean_title']
    tokenized_corpus = [simple_tokenize(doc) for doc in combined]
    return BM25Okapi(tokenized_corpus)

def search_bm25(query, top_k=10):
    """Tìm kiếm bằng BM25"""
    df = load_data_from_db()
    if df.empty:
        return []  # Nếu không có dữ liệu thì trả về rỗng

    bm25 = build_bm25_index(df)

    query = clean_text(query)
    tokenized_query = simple_tokenize(query)
    if not tokenized_query:
        return []  # Nếu query không hợp lệ

    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return df.iloc[top_indices][['title', 'content', 'date', 'source']].to_dict(orient='records')

def rerank_with_tfidf(results, query, top_rerank=3):
    """Sắp xếp lại kết quả BM25 bằng TF-IDF"""
    query_text = clean_text(query)

    if not query_text or not results:
        return []

    documents = [query_text] + [clean_text(res['title'] + " " + res['content']) for res in results]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    cosine_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    for i, res in enumerate(results):
        res["score_tfidf"] = float(cosine_scores[i])

    return sorted(results, key=lambda x: x["score_tfidf"], reverse=True)[:top_rerank]
