import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_article_content_vtv(url):
    """Lấy tiêu đề, ngày đăng, mô tả và nội dung bài viết trên VTV.vn"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Tiêu đề
    title_tag = soup.select_one("h1.title_detail")
    title = title_tag.text.strip() if title_tag else "Không có tiêu đề"

    # Mô tả (sapo)
    sapo_tag = soup.select_one("h2.sapo")
    description = sapo_tag.text.strip() if sapo_tag else ""

    # ✅ Lấy nội dung chỉ trong div id="entry-body"
    content_div = soup.find("div", {"id": "entry-body"})
    content = ''
    if content_div:
        paragraphs = content_div.find_all("p")
        for p in paragraphs:
            # Bỏ p rỗng hoặc chỉ có liên kết hoặc chứa nội dung quảng cáo
            text = p.get_text(strip=True)
            if not text:
                continue
            if "VTVGo" in text or "TV Online" in text or "mời quý độc giả" in text.lower():
                continue
            content += text + "\n"

    # Ngày đăng
    date_tag = soup.select_one("span.time")
    article_date = None
    if date_tag:
        date_text = date_tag.text
        match = re.search(r"(\d{2}/\d{2}/\d{4})", date_text)
        if match:
            try:
                article_date = datetime.strptime(match.group(1), "%d/%m/%Y").date()
            except:
                article_date = None

    full_content = f"{description}\n\n{content}".strip()
    return title, full_content, article_date


def crawl_vtv(url="https://vtv.vn/canh-bao-lua-dao.html"):
    """Crawl các bài viết từ trang VTV mục cảnh báo lừa đảo"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = []
    for a_tag in soup.select("div.tinmoi_st.timeline a[data-linktype='newsdetail']"):
        link = a_tag.get("href")
        if not link:
            continue

        if not link.startswith("http"):
            link = "https://vtv.vn" + link

        try:
            title, content, article_date = get_article_content_vtv(link)
            articles.append({
                "title": title,
                "link": link,
                "content": content,
                "date": article_date,
            })
        except Exception as e:
            print(f"❌ Lỗi khi crawl bài viết: {link}, Error: {e}")

    return articles

# def main():
#     articles = crawl_vtv()
#     for article in articles:
#         print(f"Date: {article['date']}")
#         print(f"Title: {article['title']}")
#         print(f"Link: {article['link']}")
#         print(f"Content: {article['content']}\n")

# if __name__ == "__main__":
#     main()
