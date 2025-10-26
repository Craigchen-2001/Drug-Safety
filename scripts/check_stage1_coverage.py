import os
import json
from glob import glob

base_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/affiliation_normalization"
raw_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/unique_affiliations.json"

files = sorted(glob(os.path.join(base_dir, "affiliation_normalization_batch_*.json")))

def strip_md(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t.replace("json", "", 1).strip()
        if t.endswith("```"):
            t = t[:t.rfind("```")].strip()
    return t

raw = json.load(open(raw_path, "r", encoding="utf-8"))
raw_affs = set([r["Affiliation"].strip() for r in raw])

all_members = []
seen = set()

for fp in files:
    with open(fp, "r", encoding="utf-8") as f:
        t = strip_md(f.read())
        try:
            clusters = json.loads(t)
        except:
            print(f"Cannot parse {fp}")
            continue

    members = []
    for c in clusters:
        ms = c.get("members", [])
        for m in ms:
            members.append(m.strip())
    all_members.extend(members)
    print(f"{os.path.basename(fp)} : {len(members)} members")

unique_members = set(all_members)
print("\nSummary:")
print(f"Raw unique affiliations: {len(raw_affs)}")
print(f"Stage1 total members (with duplicates): {len(all_members)}")
print(f"Stage1 unique members: {len(unique_members)}")

missing = raw_affs - unique_members
extra = unique_members - raw_affs
print(f"Missing affiliations: {len(missing)}")
print(f"Unexpected extra affiliations: {len(extra)}")

if missing:
    print("\nExample missing:", list(missing)[:10])
