import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_article_content_cafef(detail_url):
    """Lấy nội dung chi tiết bài viết từ cafef.vn"""
    response = requests.get(detail_url)
    soup = BeautifulSoup(response.content, "html.parser")

    content_div = soup.find("div", class_="detail-content afcbc-body")
    content = ""
    if content_div:
        for p in content_div.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                content += text + "\n"
    return content.strip()


def crawl_cafef(url="https://cafef.vn/thi-truong-chung-khoan.chn"):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = []
    for item in soup.select("div.tlitem-flex"):
        a_tag = item.find("a", class_="avatar")
        title = a_tag.get("title", "").strip() if a_tag else "Không có tiêu đề"
        href = a_tag.get("href", "") if a_tag else ""
        if not href:
            continue
        if not href.startswith("http"):
            link = "https://cafef.vn" + href
        else:
            link = href

        time_tag = item.select_one("span.time")
        date_str = time_tag.get("title", "") if time_tag else ""
        try:
            article_date = datetime.fromisoformat(date_str).date() if date_str else None
        except:
            article_date = None

        sapo_tag = item.select_one("p.sapo")
        sapo = sapo_tag.get_text(strip=True) if sapo_tag else ""

        try:
            content = get_article_content_cafef(link)
        except Exception as e:
            print(f"❌ Lỗi lấy nội dung từ {link}: {e}")
            content = ""

        articles.append({
            "title": title,
            "link": link,
            "sapo": sapo,
            "content": content,
            "date": article_date,
        })

    return articles

# def main():
#     articles = crawl_cafef()
#     for article in articles:
#         print(f"Date: {article['date']}")
#         print(f"Title: {article['title']}")
#         print(f"Link: {article['link']}")
#         print(f"Content: {article['content'][:500]}...\n") 

# if __name__ == '__main__':
#     main()
