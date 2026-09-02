import time
import os
import requests
from datetime import datetime, timezone
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
        response.encoding = "utf-8"
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
    all_books = []
    catalogue_pages = 0
    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    MAX_PAGES = 3

    while current_url and catalogue_pages < MAX_PAGES:
        page_number = catalogue_pages + 1
        cache_file = f"cache/catalogue-page-{page_number}.html"

        html = fetch_page(current_url, cache_file)
        book_urls, next_url = parse_catalogue_page(html, current_url)
        
        for url in book_urls:
            all_books.append({"url": url, "source_page": current_url})

        catalogue_pages += 1
        current_url = next_url

    seen = {}
    for book in all_books:
        if book["url"] not in seen:
            seen[book["url"]] = book["source_page"]
    
    unique_books = [{"url": url, "source_page": source_page} for url, source_page in seen.items()]

    print(f"catalogue pages={catalogue_pages} discovered={len(all_books)} unique_urls={len(unique_books)}")
    return unique_books

# Parsing Book Details
def parse_book_detail(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")
    product_main = soup.select_one(".product_main")

    title = product_main.select_one("h1").get_text(strip=True)
    price_text = product_main.select_one(".price_color").get_text(strip=True)
    availability_text = product_main.select_one(".instock.availability").get_text(strip=True)

    rating_tag = product_main.select_one(".star-rating")
    rating_text = rating_tag["class"][1] # e.g. ["star-rating", "Three"]

    description_heading = soup.select_one("#product_description")
    if description_heading:
        description = description_heading.find_next_sibling("p").get_text(strip=True)
    else:
        description = None

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

def extract_all_books():
    books = discover_all_books()
    records = []

    for i, book in enumerate(books):
        cache_file = f"cache/book-{i}.html"
        html = fetch_page(book["url"], cache_file)
        record = parse_book_detail(html, book["url"], book["source_page"])
        records.append(record)

    print(f"detail_pages={len(records)}")
    print(records[0])
    return records

if __name__ == "__main__":
    extract_all_books()