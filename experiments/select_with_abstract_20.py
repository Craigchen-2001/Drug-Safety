import json
import os
import random

input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/all_mesh_status.json"
output_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments"
output_path = os.path.join(output_dir, "with_abstract_20.json")

os.makedirs(output_dir, exist_ok=True)

with open(input_path, "r") as f:
    data = json.load(f)

with_abstract = [
    entry for entry in data
    if entry.get("Abstract") not in [None, "", "N/A"]
]

print("Total with Abstract:", len(with_abstract))

if len(with_abstract) >= 20:
    sample_20 = random.sample(with_abstract, 20)
else:
    raise ValueError("Not enough records with Abstract")

with open(output_path, "w") as f:
    json.dump(sample_20, f, indent=2)

print("Saved 20 samples to:", output_path)
