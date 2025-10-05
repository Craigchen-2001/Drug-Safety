import json

# 檔案路徑
file_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/all_mesh_status.json"

# 讀取 JSON
with open(file_path, "r") as f:
    data = json.load(f)

missing_abstract_ids = []

# 檢查每個 entry
for entry in data:
    abstract = entry.get("Abstract", "").strip()
    if abstract == "" or abstract.upper() == "N/A":
        missing_abstract_ids.append(entry["PMID"])

# 印出結果
print("Total records:", len(data))
print("Missing abstracts:", len(missing_abstract_ids))
print("PMIDs without abstract:")
for pmid in missing_abstract_ids:
    print(pmid)
