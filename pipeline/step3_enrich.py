"""
Step 3: Attribute Enrichment

Input  : data/clean/antiques_atlas_clean.json
Output : data/final/antiques_atlas_enriched.json

Description:
This step derives additional structured attributes for each item
based on the available title, category, and description text.
The goal is to enrich records while remaining conservative
and avoiding unsupported assumptions.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

from google import genai

# --------------------------------------------------
# File paths and runtime settings
# --------------------------------------------------

CLEAN_DATA_PATH = "data/clean/antiques_atlas_clean.json"
FINAL_DATA_PATH = "data/final/antiques_atlas_enriched.json"

MODEL_ID = "gemini-2.5-flash"
REQUEST_PAUSE_SECONDS = 0.6

# API key is embedded for assignment/demo purposes only
API_KEY = "placeholder for api key"

client = genai.Client(api_key=API_KEY)

Path("data/final").mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Prompt templates
# --------------------------------------------------

BASE_INSTRUCTIONS = """
You are an expert antique cataloguer.

Guidelines:
- Base conclusions only on the provided information.
- Avoid exact dates unless they are clearly stated.
- Prefer broad ranges when uncertainty exists.
- Use "unknown" when attribution is not possible.
- Do not invent provenance, makers, or materials.
- Respond using valid JSON only.
"""

ITEM_PROMPT_TEMPLATE = """
Generate the following attributes for the item below.

Fields to generate:
- era_or_time_period
- estimated_year_range
- region_of_origin
- functional_use
- material
- style
- short_summary
- confidence_score (0–1)

Confidence guidance:
- 0.9–1.0: clearly stated
- 0.6–0.8: strong supporting clues
- 0.3–0.5: weak inference
- <0.3: largely uncertain

Item information:
Title: {title}
Category: {category}
Description: {description}
"""

# --------------------------------------------------
# Attribute generation
# --------------------------------------------------

def generate_attributes(prompt: str) -> Dict[str, Any]:
    """
    Sends a single item prompt for attribute derivation
    and returns the parsed JSON response.
    """
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            BASE_INSTRUCTIONS,
            prompt
        ],
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
    )

    return json.loads(response.text)

# --------------------------------------------------
# Main execution
# --------------------------------------------------

def main():
    with open(CLEAN_DATA_PATH, "r", encoding="utf-8") as f:
        cleaned_items = json.load(f)

    final_records = []

    for idx, item in enumerate(cleaned_items, start=1):
        title = item.get("item_title") or "unknown"
        category = item.get("category_normalized") or "unknown"
        description = (
            item.get("description_clean")
            or item.get("description_raw")
            or "unknown"
        )

        prompt = ITEM_PROMPT_TEMPLATE.format(
            title=title,
            category=category,
            description=description,
        )

        try:
            derived = generate_attributes(prompt)
        except Exception as exc:
            print(f" X Skipped item {idx} due to error: {exc}")
            continue

        final_record = {
            # Original fields
            "source_url": item.get("source_url"),
            "item_title": title,
            "category_raw": item.get("category_raw"),
            "description_raw": item.get("description_raw"),
            "images": item.get("images"),
            "listed_price_raw": item.get("listed_price_raw"),
            "currency": item.get("currency"),
            "seller_location": item.get("seller_location"),

            # Normalized fields
            "category_normalized": category,
            "description_clean": item.get("description_clean"),
            "price_value": item.get("price_value"),

            # Enriched fields
            "era_or_time_period": derived.get("era_or_time_period"),
            "estimated_year_range": derived.get("estimated_year_range"),
            "region_of_origin": derived.get("region_of_origin"),
            "functional_use": derived.get("functional_use"),
            "material": derived.get("material"),
            "style": derived.get("style"),
            "short_summary": derived.get("short_summary"),
            "confidence_score": derived.get("confidence_score"),
        }

        final_records.append(final_record)
        print(f" - Processed {idx}/{len(cleaned_items)}: {title}")
        time.sleep(REQUEST_PAUSE_SECONDS)

    with open(FINAL_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(final_records, f, indent=2, ensure_ascii=False)

    print(
        f"\nStep 3 completed — {len(final_records)} records saved to {FINAL_DATA_PATH}"
    )

# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()
