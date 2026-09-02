import os
import requests

CACHE_FILE = "cache/catalogue-page-1.html"
URL = "https://books.toscrape.com/catalogue/page-1.html"
USER_AGENT = "FlyRankInternship-A9/1.0 (https://github.com/SeanC1801/FlyRank-intern)"

def fetch_page():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT - size: {len(html)} bytes")
        return html
    else:
        response = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Fetch failed with status {response.status_code}")

        html = response.text
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"FETCH - size: {len(html)} bytes")

        return html

if __name__ == "__main__":
    fetch_page()