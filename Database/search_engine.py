import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from rank_bm25 import BM25Okapi
import re
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Kết nối database
engine = create_engine('sqlite:///news_database.db')

def clean_text(text):
    """Chuẩn hóa văn bản"""
    return re.sub(r"[^\w\s]", "", text).strip().lower() if isinstance(text, str) else ""

def load_data_from_db():
    """Tải dữ liệu từ database"""
    df = pd.read_sql_table('news_table', con=engine).fillna('')
    return df

# Load dữ liệu từ database
df = load_data_from_db()

# Tiền xử lý dữ liệu cho BM25
df['clean_content'] = df['content'].apply(clean_text)
df['clean_title'] = df['title'].apply(clean_text)

# Tạo tập dữ liệu BM25
tokenized_corpus = [word_tokenize(doc) for doc in df['clean_content'] + " " + df['clean_title']]
bm25 = BM25Okapi(tokenized_corpus)

def search_bm25(query, top_k=10):
    """Tìm kiếm BM25 dựa trên content và title"""
    query = clean_text(query)
    tokenized_query = word_tokenize(query)

    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:top_k]  # Lấy top_k chỉ mục có điểm cao nhất

    results = df.iloc[top_indices][['title', 'content', 'date', 'source']].to_dict(orient='records')
    return results

def rerank_with_tfidf(results, query, top_rerank=3):
    """Sắp xếp lại kết quả BM25 bằng TF-IDF, chọn ra top_rerank"""
    query_text = clean_text(query)
    
    if not query_text or not results:
        return results[:top_rerank]  # Nếu không có dữ liệu, trả về top_rerank đầu tiên

    # Xây dựng tập dữ liệu TF-IDF: Truy vấn + kết quả BM25
    documents = [query_text] + [clean_text(res['title'] + " " + res['content']) for res in results]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Tính toán độ tương đồng cosine
    cosine_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    for i, res in enumerate(results):
        res["score_tfidf"] = cosine_scores[i]
    
    # Sắp xếp theo điểm TF-IDF, lấy top_rerank
    return sorted(results, key=lambda x: x["score_tfidf"], reverse=True)[:top_rerank]
