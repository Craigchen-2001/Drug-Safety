import pandas as pd  # type: ignore
import json

csv_file = input("Enter CSV file path: ").strip()
df = pd.read_csv(csv_file).fillna("N/A")

print(f"File: {csv_file}")
print("Total rows:", len(df))
print("Total columns:", len(df.columns))
print("Column names:", df.columns.tolist())

csv_pmids = set(df["PMID"].astype(str).unique())
print("Unique PMIDs in CSV:", len(csv_pmids))

json_file = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_original.json"
with open(json_file, "r", encoding="utf-8") as f:
    json_data = json.load(f)

json_pmids = set(str(item["PMID"]) for item in json_data)
print("Unique PMIDs in JSON:", len(json_pmids))

missing_in_json = csv_pmids - json_pmids
missing_in_csv = json_pmids - csv_pmids

print(f"PMIDs in your CSV but not in maude_original.json: {len(missing_in_json)}")
if missing_in_json:
    print(list(missing_in_json)[:10], "...")

print(f"PMIDs in maude_original.json but not in your CSV: {len(missing_in_csv)}")
if missing_in_csv:
    print(list(missing_in_csv)[:10], "...")
