import json

path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/pdf_tasks_no_url/pdf_task_no_url_part1.json"

with open(path, "r") as f:
    data = json.load(f)

false_items = [d for d in data if not d.get("has_pdf", False)]
pmids = [d.get("PMID") for d in false_items]

print(f"Total has_pdf = false: {len(false_items)}")
print("PMIDs:")
for p in pmids:
    print(p)
