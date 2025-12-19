"""
Step 2: Data Cleaning and Normalization

Input  : data/raw/antiques_atlas_raw.json
Output : data/clean/antiques_atlas_clean.json

Description:
This step prepares the scraped data for downstream use by:
- standardizing category labels
- cleaning free-text descriptions
- converting price strings into numeric values
- handling missing or incomplete fields safely
- removing obvious duplicate listings
"""

import json
import re
from pathlib import Path
from typing import Optional

# --------------------------------------------------
# File paths
# --------------------------------------------------

RAW_DATA_PATH = "data/raw/antiques_atlas_raw.json"
CLEAN_DATA_PATH = "data/clean/antiques_atlas_clean.json"

Path("data/clean").mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Category normalization
# --------------------------------------------------

CATEGORY_LOOKUP = {
    "Furniture": "furniture",
    "Ceramics": "ceramics",
    "Decorative Art": "decorative_art",
    "Silver": "silver",
    "Jewellery": "jewellery",
    "Lighting": "lighting",
}

def normalize_category(category: Optional[str]) -> str:
    """
    Converts human-facing category names into
    consistent, lowercase identifiers.
    """
    if not category:
        return "other"
    return CATEGORY_LOOKUP.get(category.strip(), "other")

# --------------------------------------------------
# Text cleaning
# --------------------------------------------------

def clean_description(text: Optional[str]) -> Optional[str]:
    """
    Normalizes description text by removing excess whitespace
    and discarding very short or uninformative entries.
    """
    if not text:
        return None

    text = re.sub(r"\s+", " ", text).strip()

    if len(text) < 20:
        return None

    return text

# --------------------------------------------------
# Price parsing
# --------------------------------------------------

def parse_price_value(price_text: Optional[str]) -> Optional[float]:
    if not price_text:
        return None

    price_text = price_text.lower()

    if "poa" in price_text:
        return None

    match = re.search(r"([\d,.]+)", price_text)
    if not match:
        return None

    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None

# --------------------------------------------------
# Deduplication helper
# --------------------------------------------------

def build_dedupe_key(item: dict) -> str:
    """
    Generates a lightweight key to identify
    obvious duplicate listings.
    """
    title = (item.get("item_title") or "").lower().strip()
    price = (item.get("listed_price") or "").strip()
    return f"{title[:40]}::{price}"

# --------------------------------------------------
# Cleaning pipeline
# --------------------------------------------------

def main():
    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    cleaned_items = []
    seen_keys = set()

    for item in raw_items:
        dedupe_id = build_dedupe_key(item)
        if dedupe_id in seen_keys:
            continue
        seen_keys.add(dedupe_id)

        cleaned_record = {
            # Original fields (retained for traceability)
            "source_url": item.get("source_url"),
            "item_title": item.get("item_title"),
            "category_raw": item.get("category"),
            "description_raw": item.get("description_raw"),
            "listed_price_raw": item.get("listed_price"),
            "currency": item.get("currency"),
            "seller_location": item.get("seller_location"),
            "images": item.get("images", []),

            # Normalized fields
            "category_normalized": normalize_category(item.get("category")),
            "description_clean": clean_description(item.get("description_raw")),
            "price_value": parse_price_value(item.get("listed_price")),
        }

        cleaned_items.append(cleaned_record)

    with open(CLEAN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_items, f, indent=2, ensure_ascii=False)

    print(
        f"Step 2 completed — {len(cleaned_items)} records saved to {CLEAN_DATA_PATH}"
    )

# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()
