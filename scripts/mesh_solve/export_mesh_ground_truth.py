import pandas as pd # type: ignore
import json
import os

csv_file = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_mesh.csv"
output_file = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/mesh_ground_truth.json"

df = pd.read_csv(csv_file).fillna("N/A")

mesh_terms = df["MeshTerm"].dropna().unique()
mesh_dict = {term: True for term in mesh_terms}

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(mesh_dict, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(mesh_dict)} unique MeshTerms")
print(f"Saved to {output_file}")
