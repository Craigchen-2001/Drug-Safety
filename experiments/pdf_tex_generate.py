import os
import json
from PyPDF2 import PdfReader

json_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_17.json"
pdf_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/pdf_17"

with open(json_path, "r") as f:
    data = json.load(f)

for item in data:
    pmid = item.get("PMID")
    pdf_path = os.path.join(pdf_dir, f"{pmid}.pdf")
    text_excerpt = "N/A"
    if os.path.exists(pdf_path):
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
                if len(text) > 1000:
                    break
            text_excerpt = text[:800]
        except:
            text_excerpt = "N/A"
    item["text_excerpt"] = text_excerpt

with open(json_path, "w") as f:
    json.dump(data, f, indent=2)
