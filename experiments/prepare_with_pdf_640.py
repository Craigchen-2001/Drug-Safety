import json
import os

input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/all_mesh_status.json"
existing_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_17.json"
output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_640.json"

with open(input_path, "r") as f:
    data = json.load(f)

if os.path.exists(existing_path):
    with open(existing_path, "r") as f:
        existing = json.load(f)
    existing_map = {e.get("PMID"): e for e in existing}
else:
    existing_map = {}

output = []
for entry in data:
    pmid = entry.get("PMID", "N/A")
    title = entry.get("Title", "N/A")
    abstract = entry.get("Abstract", "N/A")
    mesh_terms = entry.get("MeshTerms", [])
    if not isinstance(mesh_terms, list):
        mesh_terms = []

    pdf_url = "N/A"
    has_pdf = False
    text_excerpt = "N/A"

    if pmid in existing_map:
        old = existing_map[pmid]
        pdf_url = old.get("pdf_url", "N/A")
        has_pdf = old.get("has_pdf", False)
        text_excerpt = old.get("text_excerpt", "N/A")

    new_entry = {
        "PMID": pmid,
        "Title": title,
        "Abstract": abstract,
        "MeshTerms": mesh_terms,
        "pdf_url": pdf_url,
        "has_pdf": has_pdf,
        "text_excerpt": text_excerpt,
        "GeneratedMeshTerms_Abstract": [],
        "GeneratedMeshTerms_FullText": [],
        "FilteredOriginalMeshTerms": [],
        "RemovedOriginalMeshTerms": []
    }
    output.append(new_entry)

os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Created {len(output)} entries → {output_path}")
