import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_article_content(url):
    """Lấy nội dung và ngày đăng từ một bài viết trên Nhân Dân"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lấy nội dung bài viết
    content = ''
    for paragraph in soup.find_all('p'):
        content += paragraph.text.strip() + '\n'

    # Lấy ngày đăng bài viết từ <time class="time" datetime="YYYY-MM-DDTHH:MM:SS+0700">
    date_tag = soup.find('time', class_='time')
    if date_tag and 'datetime' in date_tag.attrs:
        date_str = date_tag['datetime']
        article_datetime = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
        article_date = article_datetime.date()
    else:
        article_date = None

    return content.strip(), article_date

def crawl_nhandan(url='https://nhandan.vn/tin-moi.html'):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('article', class_='story'):
        # Lấy tiêu đề bài viết
        title_tag = item.find('h3', class_='story__heading')
        if title_tag:
            link_tag = title_tag.find('a', class_='cms-link')
            title = title_tag.text.strip() if title_tag else "Không có tiêu đề"
            link = link_tag['href'] if link_tag else None
            
            # Xử lý link
            if link and not link.startswith('http'):
                link = 'https://nhandan.vn' + link

            # Lấy nội dung bài viết từ trang chi tiết
            content, article_date = get_article_content(link) if link else ('', None)

            articles.append({
                'title': title,
                'link': link,
                'content': content,
                'date': article_date,
            })
    
    return articles

# def main():
#     articles = crawl_nhandan()
#     for article in articles:
#         print(f"Date: {article['date']}")
#         print(f"Title: {article['title']}")
#         print(f"Link: {article['link']}")
#         print(f"Content: {article['content']}...\n")  # Giới hạn 500 ký tự để xem trước

# if __name__ == '__main__':
#     main()
