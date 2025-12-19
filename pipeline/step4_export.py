import json
import csv
from pathlib import Path

INPUT_PATH = "data/final/antiques_atlas_enriched.json"
OUTPUT_PATH = "data/final/antiques_atlas_enriched.csv"

Path("data/final").mkdir(parents=True, exist_ok=True)

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    records = json.load(f)

if not records:
    raise RuntimeError("No records found in final dataset")

fieldnames = records[0].keys()

with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in records:
        writer.writerow(row)

print(f"Step 4 complete — CSV exported to {OUTPUT_PATH}")
