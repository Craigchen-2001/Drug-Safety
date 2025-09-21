import json
import os
from openai import AzureOpenAI # type: ignore
from PyPDF2 import PdfReader# type: ignore
from tqdm import tqdm # type: ignore

api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

client = AzureOpenAI(
    api_key=api_key,
    api_version="2025-01-01-preview",
    azure_endpoint=endpoint
)
deployment_name = "gpt-4o"

def load_prompt(path):
    with open(path, "r") as f:
        return f.read()

def load_blacklist(path):
    try:
        with open(path, "r") as f:
            return set([t.lower() for t in json.load(f)])
    except:
        return set()

def extract_pdf_text(pdf_path, limit=16000):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text[:limit]
    except:
        return ""

def apply_blacklist(terms, blacklist):
    return [t for t in terms if t.lower() not in blacklist]

gen_prompt_template = load_prompt("/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/generate_mesh.txt")
filter_prompt_template = load_prompt("/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/filter_mesh.txt")
blacklist = load_blacklist("/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/blacklist.json")

input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_17.json"
pdf_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/pdf_17"

with open(input_path, "r") as f:
    data = json.load(f)

if isinstance(data, dict):
    data = [data]

print(f"Total records: {len(data)}")
print("\nRun mode:")
print("1 = Run first N records")
print("2 = Run all records")
print("3 = Run specific PMID")
run_mode = input("Enter mode (1/2/3): ").strip()

if run_mode == "1":
    n = input("Enter number of records: ").strip()
    try:
        n_to_run = min(int(n), len(data))
    except:
        n_to_run = len(data)
    records_to_process = data[:n_to_run]
elif run_mode == "2":
    records_to_process = data
elif run_mode == "3":
    pmid_input = input("Enter PMID: ").strip()
    records_to_process = [entry for entry in data if entry.get("PMID") == pmid_input]
    if not records_to_process:
        print(f"PMID {pmid_input} not found, running all records instead.")
        records_to_process = data
else:
    print("Invalid input, running all records by default.")
    records_to_process = data

print("\nSelect processing mode:")
print("1 = Title + Abstract (if Abstract missing, use text_excerpt)")
print("2 = Title + Abstract + PDF (if PDF exists)")
print("3 = Run both (Abstract-only and FullText)")
print("4 = Filter original PubMed MeshTerms")
print("5 = Run all (Generate + Filter)")
mode = input("Enter mode (1/2/3/4/5): ").strip()

for entry in tqdm(records_to_process, desc="Processing", unit="paper"):
    pmid = entry.get("PMID", "N/A")
    title = entry.get("Title", "")
    abstract = entry.get("Abstract", "") or entry.get("text_excerpt", "")
    pdf_path = os.path.join(pdf_dir, f"{pmid}.pdf")
    pdf_text = extract_pdf_text(pdf_path) if os.path.exists(pdf_path) else ""

    if mode in ["1", "3", "5"]:
        prompt_abs = gen_prompt_template.format(PMID=pmid, Title=title, Abstract=abstract, FullText="")
        resp_abs = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert in biomedical informatics and MeSH indexing."},
                {"role": "user", "content": prompt_abs},
            ],
            temperature=0
        )
        try:
            mesh_abs = json.loads(resp_abs.choices[0].message.content.strip())
            mesh_abs = apply_blacklist(mesh_abs, blacklist)
        except:
            mesh_abs = []
        if mode == "1":
            entry["GeneratedMeshTerms"] = mesh_abs
        else:
            entry["GeneratedMeshTerms_Abstract"] = mesh_abs

    if mode in ["2", "3", "5"]:
        prompt_full = gen_prompt_template.format(PMID=pmid, Title=title, Abstract=abstract, FullText=pdf_text)
        resp_full = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert in biomedical informatics and MeSH indexing."},
                {"role": "user", "content": prompt_full},
            ],
            temperature=0
        )
        try:
            mesh_full = json.loads(resp_full.choices[0].message.content.strip())
            mesh_full = apply_blacklist(mesh_full, blacklist)
        except:
            mesh_full = []
        if mode == "2":
            entry["GeneratedMeshTerms"] = mesh_full
        else:
            entry["GeneratedMeshTerms_FullText"] = mesh_full

    if mode in ["4", "5"]:
        original_mesh = [m.get("MeshTerm", "") for m in entry.get("MeshTerms", []) if isinstance(m, dict)]
        original_mesh = [t for t in original_mesh if isinstance(t, str) and t.strip()]
        prompt_filter = filter_prompt_template.format(
            PMID=pmid,
            Title=title,
            Abstract=abstract,
            FullText=pdf_text,
            OriginalMeshTerms=json.dumps(original_mesh, ensure_ascii=False)
        )
        resp_filter = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert in biomedical informatics and MeSH indexing."},
                {"role": "user", "content": prompt_filter},
            ],
            temperature=0
        )
        try:
            mesh_filter = json.loads(resp_filter.choices[0].message.content.strip())
            mesh_filter = apply_blacklist(mesh_filter, blacklist)
        except:
            mesh_filter = []
        entry["FilteredOriginalMeshTerms"] = mesh_filter
        entry["RemovedOriginalMeshTerms"] = [t for t in original_mesh if t not in mesh_filter]

with open(input_path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated file saved:", input_path)
