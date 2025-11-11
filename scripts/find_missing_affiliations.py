import json

raw_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/unique_affiliations.json"
lookup_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/affiliation_normalization/affiliation_lookup_final.json"
output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/affiliation_normalization/missing_affiliations.json"

with open(raw_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)
with open(lookup_path, "r", encoding="utf-8") as f:
    lookup = json.load(f)

raw_affs = [item["Affiliation"].strip() for item in raw_data if item.get("Affiliation")]
lookup_affs = set(k.strip() for k in lookup.keys())

missing = [a for a in raw_affs if a not in lookup_affs]

print(f"Total raw affiliations: {len(raw_affs)}")
print(f"Total mapped affiliations: {len(lookup_affs)}")
print(f"Missing affiliations: {len(missing)}")

if missing:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([{"Affiliation": m} for m in missing], f, indent=2, ensure_ascii=False)
    print(f"Missing affiliations saved to: {output_path}")
    print("Example missing:")
    for m in missing[:10]:
        print("-", m)
else:
    print("All affiliations are covered.")
