# BE-05 — The Polite Scraper

A small, polite scraping pipeline: downloads the first 3 catalogue pages of [Books to Scrape](https://books.toscrape.com), discovers all book links from those pages, visits each one, and turns the raw HTML into clean, schema-checked JSON records — surviving a broken page without crashing, and ending every run with an honest report.

## Target classification

- **Site:** Books to Scrape (https://books.toscrape.com)
- **Why this target is acceptable:** The site is designed for educational purposes and encourages scraping.
- **Scope:** 3 catalogue pages of books to scrape and then visit the first 60 individual book pages to scrape information from it.
- **Data collected:** book's title, price, stock availability, star rating, and description.
- **robots.txt result:** There were no robots.txt file found. (https://books.toscrape.com/robots.txt) returned 404 not found.

I will not reuse this code on another site without checking its rules and terms first.

## Setup and running it

```bash
cd scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

This produces `output/books.json` (60 validated records) and `output/run-report.json` (a summary of what happened). Re-running the same command is safe — it will not duplicate records, and reads previously-fetched pages from `cache/` instead of hitting the site again.

## Record schema

Each entry in `output/books.json` has this shape:

| Field | Type | Notes |
|---|---|---|
| `title` | string | |
| `product_url` | string | the record's canonical identity |
| `price_text` | string | raw price as shown on the page, e.g. `"£51.77"` |
| `price_gbp` | number | `price_text` converted to a real number, e.g. `51.77` |
| `availability_text` | string | e.g. `"In stock (22 available)"` |
| `rating_text` | string | e.g. `"Three"` |
| `description` | string or `null` | `null` when the book has no description on the page — never invented |
| `source_page` | string | which catalogue page this book was discovered on |
| `fetched_at` | string | ISO-8601 UTC timestamp of when this record was fetched |

Records that fail this schema are written to `output/errors.json` with the reason, instead of silently disappearing or corrupting `books.json`.

## Politeness rules

- **User-agent:** every real request identifies itself as `FlyRankInternship-A9/1.0`, linking to this repo, so a site owner could find out who's making the request
- **Timeout:** every request gives up after 10 seconds rather than hanging forever
- **Delay:** the scraper waits 0.5 seconds between real requests to the site; cached pages need no delay since they never leave this computer
- **Cache:** every page fetched is saved to `cache/` (git-ignored); re-running the script during development reads from there instead of asking the real site again
- **Retries:** a timeout or server error (`5xx`) gets one retry; a `404` or `403` is never retried — the page genuinely doesn't exist, or the site explicitly said no

## Why this assignment needed no browser

The data (title, price, availability, rating, description) is already present in the raw HTML the server sends back on the very first request — a browser would only add cost (rendering time, memory) without revealing anything a plain HTTP request doesn't already have.

## One real run-report.json

```json
{
  "start_time": "2026-09-02T19:40:25.825501+00:00",
  "duration_seconds": 100.83484,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

This is a genuine first-time run (no `cache/` yet) — all 63 pages (3 catalogue + 60 book pages) were real fetches, taking about 100 seconds due to the 0.5s politeness delay between each. A rerun afterward reads from `cache/` instead and finishes in well under a second.

## One honest limitation

`fetched_at` reflects the moment each record was *processed* during this run, not necessarily the original moment the page was first fetched from the real site — if a page is served from `cache/`, its content is old, but the timestamp on the record is new. A more complete version would store the fetch timestamp alongside the cached HTML itself.

## Ethics note

This scraper only touches a site explicitly built and offered for scraping practice. In any real project: check for an official API before scraping at all; never bypass a login, paywall, or an explicit block; collect only the data actually needed for the task at hand, not everything reachable.
