import time
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

USER_AGENT = "FlyRankInternship-A9/1.0 (https://github.com/SeanC1801/FlyRank-intern)"

# Fetch HTML
def fetch_page(url, cache_file):
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT - size: {len(html)} bytes")
        return html
    else:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Fetch failed with status {response.status_code}")

        html = response.text
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"FETCH - size: {len(html)} bytes")

        time.sleep(0.5)
        return html

# Parsing Page URL
def parse_catalogue_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    book_urls = []
    # finds all book links and converts each to absolute url
    for a in soup.select("article.product_pod h3 a"):
        absolute_url = urljoin(page_url, a["href"])
        book_urls.append(absolute_url)

    # find the next-page link, if there is any
    next_link = soup.select_one("li.next a")
    next_url = None
    if next_link:
        next_url = urljoin(page_url, next_link["href"])

    return book_urls, next_url

# Discover all book urls
def discover_all_books():
    all_books_url = []
    catalogue_pages = 0
    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    MAX_PAGES = 3

    while current_url and catalogue_pages < MAX_PAGES:
        page_number = catalogue_pages + 1
        cache_file = f"cache/catalogue-page-{page_number}.html"

        html = fetch_page(current_url, cache_file)
        book_urls, next_url = parse_catalogue_page(html, current_url)
        
        all_books_url.extend(book_urls)
        catalogue_pages += 1
        current_url = next_url

    unique_urls = set(all_books_url)

    print(f"catalogue pages={catalogue_pages} discovered={len(all_books_url)} unique_urls={len(unique_urls)}")
    return unique_urls




if __name__ == "__main__":
    discover_all_books()