import os
import json
import requests

input_json = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_17.json"
output_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/pdf_17"

os.makedirs(output_dir, exist_ok=True)

with open(input_json, "r") as f:
    data = json.load(f)

for record in data:
    pmid = record.get("PMID")
    pdf_url = record.get("pdf_url")
    if not pdf_url or pdf_url == "N/A":
        print(f"Skipped: {pmid}")
        continue
    try:
        response = requests.get(pdf_url, timeout=30)
        pdf_path = os.path.join(output_dir, f"{pmid}.pdf")
        with open(pdf_path, "wb") as f_out:
            f_out.write(response.content)
        print(f"Downloaded: {pmid}")
    except Exception as e:
        print(f"Error {pmid}: {e}")
