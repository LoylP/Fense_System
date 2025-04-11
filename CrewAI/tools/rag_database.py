import sys
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Database.search_engine import search_bm25, rerank_with_tfidf

load_dotenv()

def rag_db(query):
    bm25_results = search_bm25(query)
    final_results = rerank_with_tfidf(bm25_results, query)
    return final_results
