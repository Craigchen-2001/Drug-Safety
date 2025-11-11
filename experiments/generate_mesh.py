import os
import json
import re
import time
from tqdm import tqdm # type: ignore
from openai import AzureOpenAI # type: ignore



def extract_json_array(text):
    if not isinstance(text, str):
        return []
    s = text.strip()
    try:
        v = json.loads(s)
        if isinstance(v, list):
            return v
    except:
        pass
    m = re.search(r"\[[\s\S]*?\]", s)
    if m:
        try:
            v = json.loads(m.group(0))
            if isinstance(v, list):
                return v
        except:
            pass
    return []

def extractData(pdf_filepath, base_instruction, title="", abstract=""):
    try:
        assistant = client.beta.assistants.create(
            name="RAG Assistant",
            instructions=base_instruction,
            model=deployment_name,
            tools=[{"type": "file_search"}]
        )
        message_file = client.files.create(file=open(pdf_filepath, "rb"), purpose="assistants")
        user_msg = (
            "You are an expert in biomedical informatics and MeSH indexing. "
            "Use the following context and the attached PDF to extract MeSH terms. "
            "Return only a JSON array of strings (no markdown, no explanation).\n\n"
            f"Title: {title}\n\n"
            f"Abstract_or_Excerpt: {abstract}\n"
        )
        thread = client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": user_msg,
                "attachments": [{"file_id": message_file.id, "tools": [{"type": "file_search"}]}]
            }]
        )
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
        status = checkStatus(thread, run, timeout=600)
        if status != "completed":
            return {"gpt_output": "N/A", "prompt_tokens": -1, "completion_tokens": -1, "total_tokens": -1}
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        usage = getattr(run, "usage", None)
        msgs = client.beta.threads.messages.list(thread_id=thread.id).data
        for msg in reversed(msgs):
            if msg.role == "assistant":
                d = msg.model_dump()
                parts = d.get("content", [])
                collected = []
                for p in parts:
                    t = p.get("text", {})
                    if isinstance(t, dict) and "value" in t:
                        collected.append(t["value"])
                text_value = "\n".join(collected).strip()
                return {
                    "gpt_output": text_value if text_value else "N/A",
                    "prompt_tokens": getattr(usage, "prompt_tokens", -1) if usage else -1,
                    "completion_tokens": getattr(usage, "completion_tokens", -1) if usage else -1,
                    "total_tokens": getattr(usage, "total_tokens", -1) if usage else -1
                }
        return {"gpt_output": "N/A", "prompt_tokens": -1, "completion_tokens": -1, "total_tokens": -1}
    except Exception as e:
        return {"gpt_output": "N/A", "prompt_tokens": -1, "completion_tokens": -1, "total_tokens": -1}

def checkStatus(thread, run, timeout=600):
    start_time = time.time()
    status = run.status
    while status not in ["completed", "cancelled", "expired", "failed"]:
        if time.time() - start_time > timeout:
            return "timeout"
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        status = run.status
    return status

def load_prompt(path):
    with open(path, "r") as f:
        return f.read()

def load_blacklist(path):
    try:
        with open(path, "r") as f:
            return set([t.lower() for t in json.load(f)])
    except:
        return set()

def load_whitelist(path):
    try:
        with open(path, "r") as f:
            return set([t.lower() for t in json.load(f)])
    except:
        return set()

def apply_blacklist(terms, blacklist):
    return [t for t in terms if isinstance(t, str) and t.lower() not in blacklist]

def _norm(t):
    return re.sub(r'[\s;:,.]+$', '', (t or '')).strip().lower()

def restore_whitelist_and_removed(original_mesh, filtered_mesh, whitelist):
    keep_norm = set(_norm(t) for t in filtered_mesh)
    wl = set(_norm(w) for w in whitelist)
    out_filtered = []
    seen = set()
    for t in original_mesh:
        nt = _norm(t)
        if nt in keep_norm or nt in wl:
            if nt not in seen:
                out_filtered.append(t)
                seen.add(nt)
    out_removed = [t for t in original_mesh if _norm(t) not in set(_norm(x) for x in out_filtered)]
    return out_filtered, out_removed

def clean_deprecated_fields(records):
    for e in records:
        e.pop("GeneratedMeshTerms", None)

gen_prompt_template = load_prompt("/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/generate_mesh.txt")
filter_prompt_template = load_prompt("/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/filter_mesh.txt")
blacklist = load_blacklist("/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/blacklist.json")
whitelist = load_whitelist("/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/whitelist.json")

input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/with_pdf_640_merged.json"
pdf_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/all_pdf"

with open(input_path, "r") as f:
    data = json.load(f)
if isinstance(data, dict):
    data = [data]

clean_deprecated_fields(data)

print(f"Total records: {len(data)}")
print("\nRun mode:")
print("1 = Run first N records")
print("2 = Run all records")
print("3 = Run specific PMID")
print("4 = Run range of records (e.g., 108–200, skip 107)")
run_mode = input("Enter mode (1/2/3/4): ").strip()

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
    records_to_process = [entry for entry in data if str(entry.get("PMID")) == pmid_input]
    if not records_to_process:
        records_to_process = data
elif run_mode == "4":
    print(f"Valid index range: 1–{len(data)}")
    start_idx = input("Enter start index: ").strip()
    end_idx = input("Enter end index: ").strip()
    try:
        start = max(1, int(start_idx))
        end = min(int(end_idx), len(data))
        if start > end:
            start, end = end, start
        records_to_process = data[start-1:end]
    except Exception as e:
        records_to_process = data
else:
    records_to_process = data

print("\nSelect processing mode:")
print("1 = Title + Abstract")
print("2 = Title + Abstract + PDF")
print("3 = Run both (Abstract + FullText)")
print("4 = Filter original PubMed MeshTerms")
print("5 = Run all (Generate + Filter)")
mode = input("Enter mode (1/2/3/4/5): ").strip()

total_prompt_tokens = 0
total_completion_tokens = 0
total_total_tokens = 0
skipped_papers = []

for idx, entry in enumerate(tqdm(records_to_process, desc="Processing", unit="paper"), start=1):
    pmid = entry.get("PMID", "N/A")
    title = entry.get("Title", "")
    abstract = entry.get("Abstract", "") or entry.get("text_excerpt", "")
    pdf_path = os.path.join(pdf_dir, f"{pmid}.pdf")

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
        mesh_abs = extract_json_array(resp_abs.choices[0].message.content)
        mesh_abs = apply_blacklist(mesh_abs, blacklist)
        entry["GeneratedMeshTerms_Abstract"] = mesh_abs

    if mode in ["2", "3", "5"]:
        if os.path.exists(pdf_path):
            base_instruction = "Read the attached PDF along with provided title/abstract and extract a JSON array of MeSH terms only."
            res_full = extractData(pdf_path, base_instruction, title=title, abstract=abstract)
            raw_full = res_full.get("gpt_output", "").strip()
            if raw_full == "N/A":
                skipped_papers.append(pmid)
            mesh_full = extract_json_array(raw_full)
            mesh_full = apply_blacklist(mesh_full, blacklist)
            entry["GeneratedMeshTerms_FullText"] = mesh_full
            entry["FullText_prompt_tokens"] = res_full.get("prompt_tokens", -1)
            entry["FullText_completion_tokens"] = res_full.get("completion_tokens", -1)
            entry["FullText_total_tokens"] = res_full.get("total_tokens", -1)
            total_prompt_tokens += max(res_full.get("prompt_tokens", 0), 0)
            total_completion_tokens += max(res_full.get("completion_tokens", 0), 0)
            total_total_tokens += max(res_full.get("total_tokens", 0), 0)
        else:
            entry["GeneratedMeshTerms_FullText"] = []
            skipped_papers.append(pmid)

    if mode in ["4", "5"]:
        original_mesh = [m.get("MeshTerm", "") for m in entry.get("MeshTerms", []) if isinstance(m, dict)]
        original_mesh = [t for t in original_mesh if isinstance(t, str) and t.strip()]
        prompt_filter = filter_prompt_template.format(
            PMID=pmid,
            Title=title,
            Abstract=abstract,
            FullText="",
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
        mesh_filter = extract_json_array(resp_filter.choices[0].message.content)
        mesh_filter = apply_blacklist(mesh_filter, blacklist)
        filtered, removed = restore_whitelist_and_removed(original_mesh, mesh_filter, whitelist)
        entry["FilteredOriginalMeshTerms"] = filtered
        entry["RemovedOriginalMeshTerms"] = removed

    with open(input_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    time.sleep(3)

cost_prompt = total_prompt_tokens / 1000 * 0.005
cost_completion = total_completion_tokens / 1000 * 0.015
total_cost = cost_prompt + cost_completion

print("Updated file saved:", input_path)
print("\n===== Token Usage Summary =====")
print(f"Total Prompt Tokens: {total_prompt_tokens}")
print(f"Total Completion Tokens: {total_completion_tokens}")
print(f"Total Tokens: {total_total_tokens}")
print(f"Estimated Cost (GPT-4o): ${total_cost:.4f}")
print("================================")
print(f"Total skipped or failed papers: {len(skipped_papers)}")
if skipped_papers:
    print("Skipped PMIDs:", skipped_papers)
