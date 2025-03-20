import requests
from bs4 import BeautifulSoup
from datetime import datetime
import dateparser

def get_article_content_tn(url):
    """Lấy nội dung và ngày đăng từ một bài viết trên Thanh Niên"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lấy nội dung bài viết
    content = ''
    for paragraph in soup.find_all('p'):
        content += paragraph.text.strip() + '\n'

    # Lấy ngày đăng bài viết từ thẻ <time>
    date_tag = soup.find('div', {'data-role': 'publishdate'})
    if date_tag:
        date_str = date_tag.text.strip()
        article_datetime = dateparser.parse(date_str, languages=['vi'])
        article_date = article_datetime.date() if article_datetime else None
    else:
        article_date = None

    return content.strip(), article_date

def crawl_thanhnien():
    """Thu thập danh sách bài viết từ chuyên mục Chính trị của Thanh Niên"""
    url = 'https://thanhnien.vn/chinh-tri.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('div', class_='box-category-item'):
        title_tag = item.find('h3', class_='box-title-text')
        if title_tag:
            link_tag = title_tag.find('a', class_='box-category-link-title')
            if link_tag:
                title = link_tag.text.strip()
                link = link_tag['href']
                if not link.startswith('http'):
                    link = 'https://thanhnien.vn' + link

                # Lấy nội dung và ngày đăng của bài viết
                content, date = get_article_content_tn(link)

                articles.append({
                    'title': title,
                    'link': link,
                    'content': content,
                    'date': date
                })
    
    return articles

def main():
    articles = crawl_thanhnien()
    for article in articles:
        print(f"Date: {article['date']}")
        print(f"Title: {article['title']}")
        print(f"Link: {article['link']}")
        print(f"Content: {article['content'][:500]}...\n")  # Giới hạn 500 ký tự để xem trước

if __name__ == '__main__':
    main()
