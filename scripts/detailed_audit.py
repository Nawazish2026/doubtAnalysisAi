import json, re
from pathlib import Path

project_dir = Path(__file__).resolve().parents[1]

with open(Path(__file__).with_name("all_reports_dump.json"), encoding="utf-8") as f:
    items = json.load(f)

with open(project_dir / "data/taxonomy.json", encoding="utf-8") as f:
    taxonomy = json.load(f)

print(f"Total reports to audit: {len(items)}")
