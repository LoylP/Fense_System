import requests
from bs4 import BeautifulSoup
from datetime import datetime
import dateparser
import re

def get_article_content(url):
    """Lấy nội dung và ngày đăng từ một bài viết trên Báo Công An"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lấy nội dung bài viết
    content = ''
    for paragraph in soup.find_all('p'):
        content += paragraph.text.strip() + '\n'

    # Lấy ngày đăng bài viết từ thẻ <p class="hidden-xs f11 padT5 clorA">
    date_tag = soup.find('p', style="white-space: nowrap;")
    if date_tag:
        date_str = date_tag.text.strip()

        # Loại bỏ thứ và giờ, chỉ giữ lại ngày tháng năm (DD/MM/YYYY)
        match = re.search(r'(\d{2}/\d{2}/\d{4})', date_str)
        if match:
            date_cleaned = match.group(1)  # Trích xuất "19/03/2025"
            article_datetime = datetime.strptime(date_cleaned, "%d/%m/%Y").date()
        else:
            article_datetime = None
    else:
        article_datetime = None

    return content.strip(), article_datetime

def crawl_congan():
    """Thu thập danh sách bài viết từ chuyên mục Tin Chính của Báo Công An"""
    url = 'https://congan.com.vn/tin-chinh'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('li'):
        # Lấy tiêu đề bài viết
        title_tag = item.find('h3')
        if title_tag:
            link_tag = title_tag.find('a')
            title = link_tag.text.strip() if link_tag else "Không có tiêu đề"
            link = link_tag['href'] if link_tag else None
            
            # Xử lý link
            if link and not link.startswith('http'):
                link = 'https://congan.com.vn' + link
            
            # Lấy tóm tắt bài viết (summary)
            summary_tag = item.find('div', class_='hidden-xs news_lead')
            summary = summary_tag.text.strip() if summary_tag else 'Không có mô tả'

            # Lấy nội dung bài viết từ trang chi tiết
            content, article_date = get_article_content(link) if link else ('', None)

            articles.append({
                'title': title,
                'link': link,
                'summary': summary,
                'content': content,
                'date': article_date,  
            })
    
    return articles

def main():
    articles = crawl_congan()
    for article in articles:
        print(f"Date: {article['date']}")
        print(f"Title: {article['title']}")
        print(f"Link: {article['link']}")
        print(f"Summary: {article['summary']}")
        print(f"Content: {article['content'][:500]}...\n")  # Giới hạn 500 ký tự để xem trước

if __name__ == '__main__':
    main()
