import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from rank_bm25 import BM25Okapi
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    """Chuẩn hóa văn bản"""
    return re.sub(r"[^\w\s]", "", text).strip().lower() if isinstance(text, str) else ""

def simple_tokenize(text):
    """Tokenize đơn giản bằng regex"""
    return re.findall(r'\b\w+\b', text.lower())

def load_data_from_db(engine):
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

def search_bm25(query, engine, top_k=10):
    """Tìm kiếm bằng BM25"""
    df = load_data_from_db(engine)
    bm25 = build_bm25_index(df)

    query = clean_text(query)
    tokenized_query = simple_tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return df.iloc[top_indices][['title', 'content', 'date', 'source']].to_dict(orient='records')

def rerank_with_tfidf(results, query, top_rerank=3):
    """Sắp xếp lại kết quả BM25 bằng TF-IDF"""
    query_text = clean_text(query)
    
    if not query_text or not results:
        return results[:top_rerank]

    documents = [query_text] + [clean_text(res['title'] + " " + res['content']) for res in results]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    cosine_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    for i, res in enumerate(results):
        res["score_tfidf"] = float(cosine_scores[i])  # convert numpy.float to float

    return sorted(results, key=lambda x: x["score_tfidf"], reverse=True)[:top_rerank]


# DB_PATH = '/home/phuc/project/FakeBuster_System/news_database.db'
# engine = create_engine(f"sqlite:///{DB_PATH}")

# query = "ngân hàng lừa đảo AI"
# bm25_results = search_bm25(query, engine)
# final_results = rerank_with_tfidf(bm25_results, query)
# print(final_results)