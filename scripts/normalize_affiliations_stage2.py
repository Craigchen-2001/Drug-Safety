import os
import json
from glob import glob
from openai import AzureOpenAI
from tqdm import tqdm


base_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/affiliation_normalization"
prompt_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/prompts/affiliation_normalization.txt"
out_stage2_clusters = os.path.join(base_dir, "affiliation_clusters_stage2.json")
out_lookup = os.path.join(base_dir, "affiliation_lookup_final.json")

batch_size = 200

def strip_md(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t.replace("json", "", 1).strip()
        if t.endswith("```"):
            t = t[:t.rfind("```")].strip()
    return t

files = sorted(glob(os.path.join(base_dir, "affiliation_normalization_batch_*.json")))
stage1_map = {}
stage1_canonicals = []

for fp in files:
    with open(fp, "r", encoding="utf-8") as f:
        t = strip_md(f.read())
        clusters = json.loads(t)
        for c in clusters:
            cano = c["canonical"].strip()
            mems = [m.strip() for m in c.get("members", []) if isinstance(m, str)]
            if cano not in stage1_map:
                stage1_map[cano] = set()
                stage1_canonicals.append(cano)
            for m in mems:
                stage1_map[cano].add(m)

with open(prompt_path, "r", encoding="utf-8") as f:
    base_prompt = f.read().strip()

chunks = [stage1_canonicals[i:i + batch_size] for i in range(0, len(stage1_canonicals), batch_size)]
stage2_raw_clusters = []

for i, chunk in enumerate(tqdm(chunks, desc="Stage2 merging")):
    joined = "\n".join(f"- {c}" for c in chunk)
    prompt = f"{base_prompt}\n\nInput affiliations:\n{joined}"
    resp = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=8000
    )
    txt = strip_md(resp.choices[0].message.content)
    data = json.loads(txt)
    stage2_raw_clusters.extend(data)

final_clusters = []
lookup = {}

for cluster in stage2_raw_clusters:
    final_cano = cluster["canonical"].strip()
    member_canonicals = [m.strip() for m in cluster.get("members", [])]
    expanded = set()
    for mc in member_canonicals:
        if mc in stage1_map:
            expanded.update(stage1_map[mc])
        else:
            expanded.add(mc)
    expanded_list = sorted(expanded)
    final_clusters.append({"canonical": final_cano, "members": expanded_list})
    for raw in expanded_list:
        lookup[raw] = final_cano

with open(out_stage2_clusters, "w", encoding="utf-8") as f:
    json.dump(final_clusters, f, indent=2, ensure_ascii=False)

with open(out_lookup, "w", encoding="utf-8") as f:
    json.dump(lookup, f, indent=2, ensure_ascii=False)

print(f"Saved: {out_stage2_clusters}")
print(f"Saved: {out_lookup}")
