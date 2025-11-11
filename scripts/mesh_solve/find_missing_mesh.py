import json

journal_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_original.json"
mesh_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_mesh.json"

with open(journal_path, "r", encoding="utf-8") as f:
    journal_data = json.load(f)

with open(mesh_path, "r", encoding="utf-8") as f:
    mesh_data = json.load(f)

journal_pmids = {article["PMID"] for article in journal_data}
mesh_pmids = {article["PMID"] for article in mesh_data}

missing_pmids = sorted(journal_pmids - mesh_pmids)

print(f"Total PMIDs in original.json: {len(journal_pmids)}")
print(f"Total PMIDs in mesh.json: {len(mesh_pmids)}")
print(f"Missing PMIDs (no MeshTerms): {len(missing_pmids)}")
for pmid in missing_pmids:
    print(pmid)
