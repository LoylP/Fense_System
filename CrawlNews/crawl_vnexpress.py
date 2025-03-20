import requests
from bs4 import BeautifulSoup
from datetime import datetime
import dateparser

def get_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = [p.text.strip() for p in soup.find_all('p') if p.text.strip()]
    content = "\n".join(dict.fromkeys(paragraphs))

    date_tag = soup.find('span', {'class': 'date'})
    if date_tag:
        date_str = date_tag.text.strip()
        # Sử dụng dateparser để phân tích chuỗi ngày tháng
        article_datetime = dateparser.parse(date_str, languages=['vi'])
        article_date = article_datetime.date() if article_datetime else None
    else:
        article_date = None

    return content.strip(), article_date

def crawl_vnexpress(url='https://vnexpress.net/thoi-su'):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('article'):
        title_tag = item.find('h3')
        summary_tag = item.find('p')
        if title_tag and summary_tag:
            title = title_tag.text.strip()
            link = title_tag.find('a')['href']
            if not link.startswith('http'):
                link = 'https://vnexpress.net' + link
            content, date = get_article_content(link)
            articles.append({'title': title, 'link': link, 'content': content, 'date': date})
    
    return articles

# def main():
#     vnexpress_articles = crawl_vnexpress()
#     for article in vnexpress_articles:
#         print(f"Title: {article['title']}")
#         print(f"Link: {article['link']}")
#         print(f"Date: {article['date']}")
#         print(f"Content: {article['content']}")

# if __name__ == '__main__':
#     main()