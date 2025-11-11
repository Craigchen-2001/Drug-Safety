import json
import os

input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_original.json"
output_path = os.path.join(os.path.dirname(input_path), "unique_affiliations.json")

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

pmid_count = len(data)
affiliations = []
for paper in data:
    for author in paper.get("Authors", []):
        aff = author.get("Affiliation", "")
        if aff and isinstance(aff, str):
            aff = aff.strip()
            if aff:
                affiliations.append(aff)

unique_affiliations = sorted(list(set(affiliations)))
results = [{"id": i + 1, "Affiliation": aff} for i, aff in enumerate(unique_affiliations)]

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Total PMIDs: {pmid_count}")
print(f"Total unique affiliations: {len(results)}")
print(f"Output saved to: {output_path}")
