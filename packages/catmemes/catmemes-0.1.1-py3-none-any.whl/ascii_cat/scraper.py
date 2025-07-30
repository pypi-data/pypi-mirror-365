import json
import time
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://nonexistentfandomsfandom.neocities.org/'
CAST_URL = urljoin(BASE_URL, 'AAcats/cast')


def get_cat_links():
    resp = requests.get(CAST_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/AAcats/') and not href.endswith('.html'):
            links.append(urljoin(BASE_URL, href))

    return list(set(links))


def extract_ascii_from_page(url: str):
    def remove_combining_marks(text: str) -> str:
        return ''.join(
            ch
            for ch in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(ch)
        )

    def sanitize_ascii_art(text: str) -> str:
        return text.replace('\u25cc', '').replace('\u3000', '  ')

    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []

    for header in soup.find_all(['h1', 'h3']):
        next_sibling = header.find_next_sibling()
        if (
            next_sibling
            and next_sibling.name == 'div'
            and 'scrollbox' in next_sibling.get('class', [])
        ):
            span = next_sibling.find('span', class_='dqn')
            if span:
                name = header.get_text(strip=True)
                ascii_art = BeautifulSoup(
                    span.decode_contents(), 'html.parser'
                ).get_text('\n')
                results.append((name, sanitize_ascii_art(ascii_art)))

    return results


def scrape_all(output_file: str):
    all_cats = {}
    links = get_cat_links()

    for link in links:
        print(f'Scraping {link}')
        try:
            pairs = extract_ascii_from_page(link)
            for name, art in pairs:
                all_cats[name] = art
        except Exception as e:
            print(f'Failed {link}: {e}')
        time.sleep(0.3)  # be polite

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cats, f, indent=2, ensure_ascii=False)

    print(f'\nSaved {len(all_cats)} cats to cats.json')


if __name__ == '__main__':
    scrape_all('cats.json')
