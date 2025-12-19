Data Scraping & Enrichment Pipeline

Overview:-
This project implements an end-to-end data pipeline for collecting, cleaning, and enriching antique item listings.
The goal is to produce a structured, machine-ready dataset suitable for downstream use cases such as search, ranking, or identification systems.

The pipeline follows four clear stages:

Data collection from a public source

Data cleaning and normalization

Attribute enrichment

Final dataset packaging

1. Data Source

Primary source:

https://www.antiques-atlas.com

Reason for selection:

Publicly accessible (no login or paywall)

Well-structured item pages

Rich metadata available via OpenGraph and structured markup

Covers multiple antique categories (furniture, ceramics, decorative art, etc.)

2. Data Scraping (Step 1)
Approach

Category-based crawling with pagination

Per-category item limits to ensure balanced coverage

Rate limiting to avoid excessive requests

Duplicate URL tracking to prevent repeated scraping

Extracted Fields (Raw)

source_url

item_title

category

description_raw

images

listed_price

currency

seller_location

Description Handling

Item descriptions are extracted using a prioritized strategy:

OpenGraph metadata (og:description)

Structured data embedded in JSON-LD

Fallback to visible content when available

This approach provides high coverage while avoiding unreliable or incomplete HTML blocks.

3. Data Cleaning & Normalization (Step 2)

The cleaning stage prepares scraped data for structured use.

Key Operations

Category normalization
Converts human-facing category names into consistent, lowercase identifiers.

Text cleanup
Removes excess whitespace and discards uninformative descriptions.

Price parsing
Converts price strings into numeric values where possible.
Listings marked as POA are handled as missing values.

Duplicate removal
Uses a heuristic based on title and price to remove obvious duplicates.

Design Choices

Raw fields are preserved for traceability.

Cleaned fields are added alongside raw data rather than replacing it.

Missing or ambiguous values are handled gracefully instead of being guessed.

4. Attribute Enrichment (Step 3)

In this stage, additional structured attributes are derived from the available title, category, and description text.

Enriched Fields

era_or_time_period

estimated_year_range

region_of_origin

functional_use

material

style

short_summary

confidence_score

Enrichment Principles

Conservative inference only

Preference for broad ranges instead of exact dates

Use of "unknown" when attribution is not supported

Single confidence score per item (0–1) reflecting overall certainty

This ensures the dataset remains reliable and avoids over-attribution.

5. Final Dataset (Step 4)
Output Format

Primary: JSON

Optional: CSV export

Location
data/final/antiques_atlas_enriched.json


Each record contains:

Raw scraped fields

Normalized fields

Enriched attributes

JSON was chosen for flexibility and ease of integration with downstream systems.

6. Code Structure
pipeline/
- step1_scrape.py        # Data collection
- step2_clean.py         # Cleaning & normalization
- step3_enrich.py        # Attribute enrichment
- step4_export_csv.py    # (Optional) CSV export
data/
- raw/
- clean/
- final/

7. Assumptions & Limitations

Not all listings provide complete descriptions or pricing

Region and era inference may be limited by available metadata

Deduplication is heuristic, not semantic

Enrichment is intentionally conservative to avoid incorrect attribution

8. Scaling Considerations

To scale this pipeline to 50k–100k items:

Use asynchronous HTTP requests or a job queue

Persist intermediate results in a database or object storage

Add retry logic and request backoff

Batch enrichment requests

Introduce structured logging and monitoring

The current design already separates concerns cleanly, making scaling straightforward.

Conclusion

This pipeline demonstrates a practical approach to building high-quality structured datasets from public web sources.
It emphasizes correctness, traceability, and conservative reasoning over aggressive inference, ensuring the final dataset is suitable for real-world use.

