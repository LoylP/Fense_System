import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_article_content_antv(link):
    """Lấy nội dung chi tiết bài viết trên ANTV trong div.detail-article"""
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    content = ""
    detail_div = soup.find("div", class_="detail-article")
    if detail_div:
        for p in detail_div.find_all("p"):
            text = p.get_text(strip=True)
            if text and "ANTV" not in text and "VTVGo" not in text and "TV Online" not in text:
                content += text + "\n"

    return content.strip()

def crawl_antv(url="https://antv.gov.vn/su-kien/tham-hoa-hang-khong-62.html"):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []

    for item in soup.select("article.article-horizontal"):
        title_tag = item.select_one("h2 a.title-link")
        sapo_tag = item.select_one("p.sapo")
        time_tag = item.select_one("span.time-published")

        if not title_tag or not title_tag.get("href"):
            continue

        title = title_tag.get("title", "").strip()
        detail_link = title_tag["href"]
        if not detail_link.startswith("http"):
            detail_link = "https://antv.gov.vn" + detail_link

        sapo = sapo_tag.text.strip() if sapo_tag else ""
        date_str = time_tag.text.strip() if time_tag else ""
        try:
            article_date = datetime.strptime(date_str, "%d/%m/%Y").date() if date_str else None
        except:
            article_date = None

        try:
            content = get_article_content_antv(detail_link)
        except Exception as e:
            print(f"❌ Lỗi khi lấy nội dung bài viết: {detail_link}, Error: {e}")
            content = ""

        articles.append({
            "title": title,
            "link": detail_link,
            "sapo": sapo,
            "content": content,
            "date": article_date,
        })

    return articles


# def main():
#     articles = crawl_antv()
#     for article in articles:
#         print(f"Date: {article['date']}")
#         print(f"Title: {article['title']}")
#         print(f"Link: {article['link']}")
#         print(f"Content: {article['content'][:500]}...\n") 

# if __name__ == '__main__':
#     main()
