import time
import os
import requests
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydantic import BaseModel
from typing import Optional

USER_AGENT = "FlyRankInternship-A9/1.0 (https://github.com/SeanC1801/FlyRank-intern)"
stats = {"pages_fetched": 0, "cache_hits": 0}

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str]
    source_page: str
    fetched_at: str

# Fetch HTML
def fetch_page(url, cache_file):
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT - size: {len(html)} bytes")
        stats["cache_hits"] += 1
        return html
    
    for attempt in range(2):
        try: 
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        except requests.exceptions.Timeout:
            if attempt == 0:
                time.sleep(1)
                continue
            else:
                raise Exception(f"Timeout on {url} after retrying")

        if response.status_code == 200:
            response.encoding = "utf-8"
            html = response.text
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"FETCH - size: {len(html)} bytes")
            time.sleep(0.5)
            stats["pages_fetched"] += 1
            return html

        if response.status_code in (404, 403):
            raise Exception(f"Fetch failed with status {response.status_code} (not retrying): {url}")

        if response.status_code >= 500 and attempt == 0:
            time.sleep(1)
            continue

        raise Exception(f"Fetch failed with status {response.status_code} (not retrying): {url}")

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

# Extract all details in a book
def extract_all_books():
    books = discover_all_books()
    records = []
    failed_pages = 0    

    for i, book in enumerate(books):
        cache_file = f"cache/book-{i}.html"
        try:
            html = fetch_page(book["url"], cache_file)
            record = parse_book_detail(html, book["url"], book["source_page"])
            records.append(record)
        except Exception as e:
            failed_pages += 1
            print(f"Failed to fetch or parse book {book['url']}: {e}")

    print(f"detail_pages={len(records)} failed_pages={failed_pages}")
    return records, failed_pages

def parse_price(price_text):
    return float(price_text.replace("£", "").strip())

def validate_and_store(records):
    os.makedirs("output", exist_ok=True)
    valid = []
    errors = []

    for record in records:
        try:
            record["price_gbp"] = parse_price(record["price_text"])
            validated = BookRecord(**record)
            valid.append(validated.model_dump())
        except Exception as e:
            errors.append({"record": record, "reason": str(e)})

    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(valid, f, indent=2, ensure_ascii=False)

    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)

    print(f"valid_records={len(valid)} invalid_records={len(errors)}")
    return valid, errors

if __name__ == "__main__":
    start_time = datetime.now(timezone.utc)

    records, failed_pages = extract_all_books()
    valid, errors = validate_and_store(records)

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    report = {
        "start_time": start_time.isoformat(),
        "duration_seconds": duration,
        "pages_fetched": stats["pages_fetched"],
        "cache_hits": stats["cache_hits"],
        "valid_records": len(valid),
        "invalid_records": len(errors),
        "failed_pages": failed_pages,
    }

    with open("output/run-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(report)