import json

original_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_original.json"
mesh_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_mesh.json"

with open(original_path, "r", encoding="utf-8") as f:
    original_data = json.load(f)

with open(mesh_path, "r", encoding="utf-8") as f:
    mesh_data = json.load(f)

print("Total rows in original:", len(original_data))
unique_pmids = {article["PMID"] for article in original_data}
print("Total unique PMIDs in original:", len(unique_pmids))

mesh_dict = {article["PMID"]: article.get("MeshTerms", []) for article in mesh_data}

missing = []
all_status = []

for article in original_data:
    pmid = article["PMID"]
    entry = {
        "PMID": pmid,
        "Title": article.get("Title", "N/A"),
        "Abstract": article.get("Abstract", "N/A"),
    }
    if pmid in mesh_dict and mesh_dict[pmid]:
        entry["MeshTerms"] = mesh_dict[pmid]
    else:
        entry["MeshTerms"] = "N/A"
        missing.append(entry)
    all_status.append(entry)

with open("/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/missing_mesh.json", "w", encoding="utf-8") as f:
    json.dump(missing, f, ensure_ascii=False, indent=2)

with open("/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/all_mesh_status.json", "w", encoding="utf-8") as f:
    json.dump(all_status, f, ensure_ascii=False, indent=2)

print(f"Exported {len(missing)} missing entries to missing_mesh.json")
print(f"Exported {len(all_status)} total entries to all_mesh_status.json")
