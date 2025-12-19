"""
Step 1: Data Collection

Source:
https://www.antiques-atlas.com

Description:
This script collects antique item listings from multiple public categories
on Antiques Atlas. For each item, it extracts basic listing details such as
title, description, images, price, and seller location.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# --------------------------------------------------
# Configuration
# --------------------------------------------------

RAW_OUTPUT_PATH = "data/raw/antiques_atlas_raw.json"
BASE_SITE_URL = "https://www.antiques-atlas.com"

CATEGORY_PATHS = {
    "Furniture": "/antiques/furniture/",
    "Ceramics": "/antiques/ceramics/",
    "Decorative Art": "/antiques/decorative/",
    "Silver": "/antiques/silver/",
    "Jewellery": "/antiques/jewellery/",
    "Lighting": "/antiques/lighting/",
}

MAX_ITEMS_PER_CATEGORY = 30
MAX_PAGES_TO_SCAN = 30
REQUEST_PAUSE_SECONDS = 0.7

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TrackzioAssignmentBot/1.0)"
}

Path("data/raw").mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Scraping logic
# --------------------------------------------------

collected_items = []
visited_item_urls = set()

for category_name, category_path in CATEGORY_PATHS.items():
    print(f"\nScraping category: {category_name}")
    items_collected = 0
    page_number = 1

    while items_collected < MAX_ITEMS_PER_CATEGORY and page_number <= MAX_PAGES_TO_SCAN:
        category_url = f"{BASE_SITE_URL}{category_path}?page={page_number}"
        response = requests.get(
            category_url,
            headers=REQUEST_HEADERS,
            timeout=15
        )

        soup = BeautifulSoup(response.text, "html.parser")
        item_links = soup.select("a[href^='/antique/']")

        if not item_links:
            break

        for link in item_links:
            if items_collected >= MAX_ITEMS_PER_CATEGORY:
                break

            relative_url = link.get("href")
            if not relative_url:
                continue

            item_url = BASE_SITE_URL + relative_url
            if item_url in visited_item_urls:
                continue

            visited_item_urls.add(item_url)

            try:
                item_response = requests.get(
                    item_url,
                    headers=REQUEST_HEADERS,
                    timeout=15
                )
                item_page = BeautifulSoup(item_response.text, "html.parser")

                # --------------------------------------------------
                # Basic item details
                # --------------------------------------------------

                title_tag = item_page.find("h1")
                item_title = title_tag.get_text(strip=True) if title_tag else None

                # --------------------------------------------------
                # Description extraction
                # --------------------------------------------------

                description_text = None

                og_description = item_page.find(
                    "meta", property="og:description"
                )
                if og_description and og_description.get("content"):
                    description_text = og_description["content"].strip()

                if not description_text:
                    json_ld = item_page.find(
                        "script", type="application/ld+json"
                    )
                    if json_ld:
                        try:
                            structured_data = json.loads(json_ld.string)
                            if isinstance(structured_data, dict):
                                description_text = structured_data.get("description")
                        except Exception:
                            pass

                # --------------------------------------------------
                # Price and seller location
                # --------------------------------------------------

                price_tag = item_page.find("span", class_="price")
                listed_price = (
                    price_tag.get_text(strip=True) if price_tag else None
                )

                location_tag = item_page.find(
                    "span", class_="dealer-location"
                )
                seller_location = (
                    location_tag.get_text(strip=True)
                    if location_tag else None
                )

                # --------------------------------------------------
                # Image collection
                # --------------------------------------------------

                image_urls = []
                for img in item_page.find_all("img"):
                    src = img.get("src") or img.get("data-src")
                    if not src:
                        continue

                    if src.startswith("//"):
                        src = "https:" + src

                    if "images.antiquesatlas.com" in src:
                        image_urls.append(src)

                image_urls = list(dict.fromkeys(image_urls))[:5]

                # --------------------------------------------------
                # Store record
                # --------------------------------------------------

                collected_items.append({
                    "source_url": item_url,
                    "item_title": item_title,
                    "category": category_name,
                    "description_raw": description_text,
                    "images": image_urls,
                    "listed_price": listed_price,
                    "currency": "GBP",
                    "seller_location": seller_location,
                })

                items_collected += 1
                print(f"{item_title}")
                time.sleep(REQUEST_PAUSE_SECONDS)

            except Exception as exc:
                print(f"Failed to process {item_url}: {exc}")

        page_number += 1

# --------------------------------------------------
# Save results
# --------------------------------------------------

with open(RAW_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(collected_items, f, indent=2, ensure_ascii=False)

print(
    f"\nStep 1 completed — {len(collected_items)} items saved to {RAW_OUTPUT_PATH}"
)
