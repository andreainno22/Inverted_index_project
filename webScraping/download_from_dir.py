import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://www.gutenberg.org"
START_URL = f"{BASE_URL}/ebooks/bookshelf/427"
DOWNLOAD_FOLDER = "gutenberg_Biographies_txt"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0'}


def get_book_links_from_page(url):
    """Extracts all book links from a category page."""
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    books = soup.select('li.booklink a.link')
    return [BASE_URL + book['href'] for book in books]


def get_next_page_url(soup):
    next_link = soup.find('a', string="Next")
    if next_link:
        return BASE_URL + next_link['href']
    return None


def find_txt_download_link(book_url):
    """Searches for the .txt.utf-8 download link on a book's page."""
    resp = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        if '.txt.utf-8' in a['href']:
            href = a['href']
            return href if href.startswith('http') else BASE_URL + href
    return None


# Initialize multi-page scraping
current_page_url = START_URL
book_urls = []

while current_page_url:
    print(f"Visiting category page: {current_page_url}")
    resp = requests.get(current_page_url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    book_urls += get_book_links_from_page(current_page_url)
    current_page_url = get_next_page_url(soup)
    time.sleep(1)

# Download books
print(f"\nFound {len(book_urls)} books. Starting download...\n")
for book_url in book_urls:
    print(f"Book page: {book_url}")
    txt_link = find_txt_download_link(book_url)
    if txt_link:
        filename = txt_link.split('/')[-1]
        print(f"Downloading {filename}")
        txt_data = requests.get(txt_link, headers=headers)
        with open(os.path.join(DOWNLOAD_FOLDER, filename), 'wb') as f:
            f.write(txt_data.content)
        time.sleep(1)
    else:
        print("No .txt.utf-8 file found.")
