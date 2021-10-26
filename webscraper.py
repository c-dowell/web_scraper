import string
import os
import requests
from bs4 import BeautifulSoup


def create_title(soup):
    """Create and return the document title from soup object"""
    find_title = soup.find('h1', {'itemprop': 'headline'}).text
    exclude = set(string.punctuation)
    tran_tab = str.maketrans(' ', '_')
    title: str = ''.join(ch for ch in find_title if ch not in exclude).translate(tran_tab)
    return title


num_pages = int(input())
article_type = input()
cwd = os.getcwd()
ok = False

for page in range(1, num_pages + 1):
    url = f'https://www.nature.com/nature/articles?searchType=journal' \
          f'Search&sort=PubDate&page={page}'
    r = requests.get(url)
    # Make and switch to a directory for each new page
    if not os.access(os.path.join(cwd, f'Page_{page}'), os.R_OK):
        os.mkdir(os.path.join(cwd, f'Page_{page}'))
    os.chdir(os.path.join(cwd, f'Page_{page}'))
    if r.status_code == 200:
        # Find all articles in webpage
        article_soup = BeautifulSoup(r.content, 'html.parser')
        articles = article_soup.find_all('article', {'itemtype': 'http://schema.org/ScholarlyArticle'})
        for article in articles:
            # For each article, find it's type
            find_article_type = article.find('span', {'class': 'c-meta__type'})
            if article_type in find_article_type:
                # Filter by chosen article type
                a_url = f"https://www.nature.com{article.a.get('href')}"
                r2 = requests.get(a_url)
                if r2.status_code:
                    # Navigate to each article's URL
                    sub_soup = BeautifulSoup(r2.content, 'html.parser')
                    article_title = create_title(sub_soup).strip()
                    print(article_title)
                    if 'News' in article_type:
                        article_body = sub_soup.find('div', {'class': 'c-article-body u-clearfix'})
                    else:
                        article_body = sub_soup.find('div', {'class': 'article-item__body'})
                    # Save body of article to file
                    if article_body:
                        save_file = open(f'{article_title}.txt', 'wb')
                        save_file.write(bytes(article_body.text.strip().encode()))
                        save_file.close()
    ok = True

if not ok:
    print(f'The URL returned {r.status_code}')
