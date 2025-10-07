import json

path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_640_merged.json"

with open(path, "r") as f:
    data = json.load(f)

no_pdf = [d for d in data if not d.get("has_pdf", False)]
no_abstract = [d for d in no_pdf if d.get("Abstract") in [None, "", "N/A"]]

print(f"Total has_pdf = false: {len(no_pdf)}")
print(f"No Abstract: {len(no_abstract)}\n")

for d in no_abstract:
    print(f"PMID: {d.get('PMID')} | Title: {d.get('Title')}")
