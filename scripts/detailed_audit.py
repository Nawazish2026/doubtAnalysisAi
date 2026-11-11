import json, re

with open("acadza-report-fix/all_reports_dump.json") as f:
    items = json.load(f)

with open("acadza-report-fix/data/taxonomy.json") as f:
    taxonomy = json.load(f)

print(f"Total reports to audit: {len(items)}")
