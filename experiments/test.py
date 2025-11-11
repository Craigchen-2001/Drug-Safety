import json

json_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_640_merged.json"

with open(json_path, "r") as f:
    data = json.load(f)

if isinstance(data, dict):
    data = [data]

def is_empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower() in ["", "n/a", "na"]
    if isinstance(v, list):
        return len(v) == 0 or all(str(x).strip().lower() in ["", "n/a", "na"] for x in v)
    return False

both_missing_ids = []
both_missing_no_original_ids = []

for entry in data:
    pmid = str(entry.get("PMID", "")).strip()
    abs_terms = entry.get("GeneratedMeshTerms_Abstract", [])
    full_terms = entry.get("GeneratedMeshTerms_FullText", [])
    original_mesh = entry.get("MeshTerms", [])

    abs_empty = is_empty(abs_terms)
    full_empty = is_empty(full_terms)
    original_empty = is_empty(original_mesh)

    # 1️⃣ Both Abstract and PDF missing
    if abs_empty and full_empty:
        both_missing_ids.append(pmid)
        # 2️⃣ Also no original MeshTerms
        if original_empty:
            both_missing_no_original_ids.append(pmid)

print("===== Both Abstract and PDF results missing =====")
print(f"Total entries: {len(data)}")
print(f"Count (Both missing): {len(both_missing_ids)}")
print("=================================================\n")

for i in range(0, len(both_missing_ids), 6):
    print(" ".join(both_missing_ids[i:i+6]))

print("\n===== Both missing AND no original MeshTerms =====")
print(f"Count (Both missing + no original Mesh): {len(both_missing_no_original_ids)}")
print("===================================================\n")

for i in range(0, len(both_missing_no_original_ids), 6):
    print(" ".join(both_missing_no_original_ids[i:i+6]))
