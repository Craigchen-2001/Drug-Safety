import json
import os
import math

input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_640.json"
output_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/pdf_tasks_no_url"

os.makedirs(output_dir, exist_ok=True)

with open(input_path, "r") as f:
    data = json.load(f)

def has_valid_url(v):
    if not v:
        return False
    if not isinstance(v, str):
        return False
    return v.strip().lower() != "n/a" and v.strip() != ""

no_pdfurl = [d for d in data if not has_valid_url(d.get("pdf_url"))]
total_no_url = len(no_pdfurl)
print(f"Total papers without pdf_url: {total_no_url}")

part_size = math.ceil(total_no_url / 3) if total_no_url > 0 else 0
parts = [no_pdfurl[i:i + part_size] for i in range(0, total_no_url, part_size)] if part_size else [[], [], []]
while len(parts) < 3:
    parts.append([])

counts = {}
for idx, part in enumerate(parts[:3], 1):
    output_path = os.path.join(output_dir, f"pdf_task_no_url_part{idx}.json")
    task_data = [
        {
            "PMID": d.get("PMID", "N/A"),
            "Title": d.get("Title", "N/A"),
            "pdf_url": d.get("pdf_url", "N/A"),
            "has_pdf": False
        }
        for d in part
    ]
    with open(output_path, "w") as f:
        json.dump(task_data, f, indent=2, ensure_ascii=False)
    counts[f"pdf_task_no_url_part{idx}.json"] = len(task_data)

print("\nSummary (IDs per file):")
for name, count in counts.items():
    print(f"{name}: {count} IDs")
print(f"\nTotal IDs across parts: {sum(counts.values())}")
