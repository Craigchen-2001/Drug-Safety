import os
import json
from openai import AzureOpenAI
from tqdm import tqdm


input_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/unique_affiliations.json"
prompt_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/prompts/affiliation_normalization.txt"
output_dir = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/affiliation_normalization"
batch_size = 80

os.makedirs(output_dir, exist_ok=True)

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(prompt_path, "r", encoding="utf-8") as f:
    base_prompt = f.read().strip()

chunks = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]

total_members = 0
for i, chunk in enumerate(tqdm(chunks, desc="Processing batches")):
    affiliations = [item["Affiliation"] for item in chunk if item.get("Affiliation")]
    joined = "\n".join(f"- {a}" for a in affiliations)
    prompt = f"{base_prompt}\n\nInput affiliations:\n{joined}"

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=8000,
    )

    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```"):
        result_text = result_text.strip("`")
        result_text = result_text.replace("json", "", 1).strip()
        if result_text.endswith("```"):
            result_text = result_text[:result_text.rfind("```")].strip()

    out_path = os.path.join(output_dir, f"affiliation_normalization_batch_{i+1:02d}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result_text)

    try:
        clusters = json.loads(result_text)
        members = [m.strip() for c in clusters for m in c.get("members", [])]
        print(f"Batch {i+1} members: {len(members)}")
        total_members += len(members)
    except Exception as e:
        print(f"Batch {i+1} parse error: {e}")

print(f"\nTotal members across all batches: {total_members}")
print(f"Expected total affiliations: 1374")
