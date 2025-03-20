import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_article_content(url):
    """Lấy nội dung và ngày đăng từ một bài viết trên Dân Trí"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lấy nội dung bài viết
    content = ''
    for paragraph in soup.find_all('p'):
        content += paragraph.text.strip() + '\n'

    # Lấy ngày đăng bài viết từ <time class="author-time" datetime="YYYY-MM-DD HH:MM">
    date_tag = soup.find('time', class_='author-time')
    if date_tag and 'datetime' in date_tag.attrs:
        date_str = date_tag['datetime']
        article_datetime = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        article_date = article_datetime.date()
    else:
        article_date = None

    return content.strip(), article_date

def crawl_dantri():
    """Thu thập danh sách bài viết từ chuyên mục mới nhất của Dân Trí"""
    url = 'https://dantri.com.vn/tin-moi-nhat.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('article', class_='article-list'):
        # Lấy tiêu đề bài viết
        title_tag = item.find('h3', class_='article-title')
        if title_tag:
            title = title_tag.text.strip()
            
            # Lấy link bài viết
            link_tag = title_tag.find('a')
            link = link_tag['href'] if link_tag else None
            if link and not link.startswith('http'):
                link = 'https://dantri.com.vn' + link
        
            # Lấy nội dung bài viết từ trang chi tiết
            content, article_date = get_article_content(link) if link else ('', None)

            articles.append({
                'title': title,
                'link': link,
                'content': content,
                'date': article_date,  
            })
    
    return articles

def main():
    articles = crawl_dantri()
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Link: {article['link']}")
        print(f"Date: {article['date']}")
        print(f"Content: {article['content'][:500]}...\n")  # Giới hạn 500 ký tự để xem trước

if __name__ == '__main__':
    main()
