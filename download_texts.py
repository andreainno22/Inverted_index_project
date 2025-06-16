import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://www.gutenberg.org"
TOP_URL = f"{BASE_URL}/ebooks/bookshelf/441"
DOWNLOAD_FOLDER = "gutenberg_txt_health_medicine"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0'}

# Fase 1: Ottieni la pagina Top 100
resp = requests.get(TOP_URL, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# Fase 2: Trova link ai libri nella sezione "Top 100 EBooks yesterday"
#top_books_section = soup.find('h2', string="Top 100 EBooks yesterday").find_next('ol')
#top_books_section = soup.find('h2', string="Top 100 EBooks last 7 days").find_next('ol')
top_books_section = soup.find('h2', string="Displaying results 1–25 | Next").find_next('ol')

book_links = top_books_section.find_all('a')

for link in book_links:
    book_page = BASE_URL + link.get('href')
    print(f"Visiting: {book_page}")
    book_resp = requests.get(book_page, headers=headers)
    book_soup = BeautifulSoup(book_resp.text, 'html.parser')

    # Cerca un link al .txt (plain text UTF-8 preferito)
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