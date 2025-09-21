import json
import pandas as pd

input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_17.json"
output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_17.csv"

with open(input_path, "r") as f:
    data = json.load(f)

if isinstance(data, dict):
    data = [data]

rows = []
for entry in data:
    row = {
        "PMID": entry.get("PMID", ""),
        "Title": entry.get("Title", ""),
        "Abstract": entry.get("Abstract", ""),
        "pdf_url": entry.get("pdf_url", ""),
        "has_pdf": entry.get("has_pdf", ""),
        "text_excerpt": entry.get("text_excerpt", "")
    }

    # 原始 PubMed MeshTerms
    mesh_terms = []
    for m in entry.get("MeshTerms", []):
        if isinstance(m, dict):
            mesh_terms.append(m.get("MeshTerm", ""))
        elif isinstance(m, str):
            mesh_terms.append(m)
    row["MeshTerms"] = "; ".join(mesh_terms)

    def normalize_list(val):
        return "; ".join(val) if isinstance(val, list) else ""

    # LLM 生成的 MeshTerms
    row["GeneratedMeshTerms"] = normalize_list(entry.get("GeneratedMeshTerms", []))
    row["GeneratedMeshTerms_Abstract"] = normalize_list(entry.get("GeneratedMeshTerms_Abstract", []))
    row["GeneratedMeshTerms_FullText"] = normalize_list(entry.get("GeneratedMeshTerms_FullText", []))

    # Filtered + Removed (新增匯出)
    row["FilteredOriginalMeshTerms"] = normalize_list(entry.get("FilteredOriginalMeshTerms", []))
    row["RemovedOriginalMeshTerms"] = normalize_list(entry.get("RemovedOriginalMeshTerms", []))

    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"CSV saved to {output_path}")
