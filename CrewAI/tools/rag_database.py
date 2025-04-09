import sys
import os
from sqlalchemy import create_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Database.search_engine import search_bm25, rerank_with_tfidf

def rag_db(query):
    DB_PATH = '/home/phuc/project/FakeBuster_System/news_database.db'
    engine = create_engine(f"sqlite:///{DB_PATH}")
    bm25_results = search_bm25(query, engine)
    final_results = rerank_with_tfidf(bm25_results, query)
    return final_results
