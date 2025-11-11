import json

raw_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_original.json"
lookup_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/affiliation_normalization/affiliation_lookup_final.json"
output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/maude_with_normalized_affiliations.json"

with open(lookup_path, "r") as f:
    lookup = json.load(f)

with open(raw_path, "r") as f:
    data = json.load(f)

missing = []
total_count = 0

for paper in data:
    if "Authors" in paper:
        for author in paper["Authors"]:
            aff = author.get("Affiliation", "").strip()
            total_count += 1
            new_aff = lookup.get(aff, "N/A")
            if new_aff == "N/A":
                missing.append(aff)
            author["new_Affiliation"] = new_aff

with open(output_path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Total affiliations checked: {total_count}")
print(f"Unmatched (N/A): {len(missing)}")
print(f"Matched: {total_count - len(missing)}")

if missing:
    print("\nUnmatched affiliations:")
    for aff in missing:
        print("-", aff)
