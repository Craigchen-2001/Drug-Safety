import os
import json
from openai import AzureOpenAI
from PyPDF2 import PdfReader
from time import sleep



input_json = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/maude_with_normalized_affiliations.json"
output_json = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/maude_with_normalized_affiliations_abstract_updated.json"
prompt_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/generate_abstract_prompt.txt"
pdf_folder = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/all_pdf"

with open(prompt_path, "r") as f:
    base_prompt = f.read()

with open(input_json, "r") as f:
    data = json.load(f)

missing_items = [item for item in data if item.get("Abstract") == "N/A"]
total_missing = len(missing_items)
print(f"Total missing abstracts: {total_missing}")

success_count = 0
missing_pdf_count = 0
error_count = 0

for idx, item in enumerate(missing_items, start=1):
    pmid = item.get("PMID")
    pdf_path = os.path.join(pdf_folder, f"{pmid}.pdf")
    print(f"[{idx}/{total_missing}] Processing PMID {pmid} ...", end=" ")

    if not os.path.exists(pdf_path):
        item["Abstract"] = "LLM-Error: PDF not found"
        missing_pdf_count += 1
        print("PDF missing.")
        continue

    try:
        reader = PdfReader(pdf_path)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
        content = base_prompt + "\n\nPaper content:\n" + pdf_text[:15000]
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": content}],
            max_tokens=600
        )
        abstract = response.choices[0].message.content.strip()
        item["Abstract"] = abstract
        success_count += 1
        print("done.")
    except Exception as e:
        item["Abstract"] = f"LLM-Error: {str(e)}"
        error_count += 1
        print("error.")

    sleep(1)

with open(output_json, "w") as f:
    json.dump(data, f, indent=2)

print("\nGeneration completed.")
print(f"Successfully generated: {success_count}")
print(f"Missing PDFs: {missing_pdf_count}")
print(f"Errors: {error_count}")
print(f"Output saved to: {output_json}")
