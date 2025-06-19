import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://www.gutenberg.org"
TOP_URL = f"{BASE_URL}/browse/scores/top"
DOWNLOAD_FOLDER = "gutenberg_txt_top_100"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0'}

# Phase 1: Get the top bookshelf page
resp = requests.get(TOP_URL, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# Phase 2: Find links to books in the "Top 100 EBooks yesterday" section
top_books_section = soup.find('h2', string="Top 100 EBooks yesterday").find_next('ol')

book_links = top_books_section.find_all('a')

for link in book_links:
    book_page = BASE_URL + link.get('href')
    print(f"Visiting: {book_page}")
    book_resp = requests.get(book_page, headers=headers)
    book_soup = BeautifulSoup(book_resp.text, 'html.parser')

    # Look for a link to the .txt file (preferably plain text UTF-8)
    txt_link = None
    for a in book_soup.find_all('a'):
        if 'Plain Text UTF-8' in a.text and '.txt' in a['href']:
            txt_link = a['href']
            break
        elif 'Plain Text' in a.text and '.txt' in a['href']:
            txt_link = a['href']

    if txt_link:
        full_txt_url = txt_link if txt_link.startswith('http') else BASE_URL + txt_link
        file_name = full_txt_url.split('/')[-1]
        print(f"→ Downloading {file_name}")
        txt_data = requests.get(full_txt_url, headers=headers)
        with open(os.path.join(DOWNLOAD_FOLDER, file_name), 'wb') as f:
            f.write(txt_data.content)
        time.sleep(1)
    else:
        print("→ No .txt link found.")
