import os
import json
from openai import AzureOpenAI
from time import sleep
from tqdm import tqdm
from collections import Counter


input_json = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/maude_with_normalized_affiliations_abstract_updated.json"
output_json = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/maude_with_normalized_affiliations_topic_labeled.json"
prompt_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/prompts/classify_medical_topic_prompt.txt"
pdf_folder = "/Users/chenweichi/Desktop/Drug_Safety_Project/experiments/all_pdf"

with open(prompt_path, "r") as f:
    base_prompt = f.read()

with open(input_json, "r") as f:
    data = json.load(f)

total = len(data)
print(f"Total papers available: {total}")
num_to_run = int(input("How many papers do you want to process? "))
if num_to_run > total:
    num_to_run = total

success_count = 0
error_count = 0

for idx, item in enumerate(tqdm(data[:num_to_run], desc="Processing papers"), start=1):
    pmid = str(item.get("PMID"))
    title = item.get("Title", "")
    abstract = item.get("Abstract", "")
    pdf_path = os.path.join(pdf_folder, f"{pmid}.pdf")

    if not os.path.exists(pdf_path):
        item["topic"] = "N/A"
        continue

    try:
        message_file = client.files.create(
            file=open(pdf_path, "rb"),
            purpose="assistants"
        )

        assistant = client.beta.assistants.create(
            name="Medical Topic Classifier",
            instructions=base_prompt,
            model=deployment_name,
            tools=[{"type": "file_search"}]
        )

        thread = client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": f"Please classify the medical topic for this paper.\n\nTitle:\n{title}\n\nAbstract:\n{abstract}",
                "attachments": [
                    {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                ]
            }]
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status in ["completed", "failed", "cancelled"]:
                break
            sleep(2)

        if run_status.status != "completed":
            item["topic"] = "N/A"
            error_count += 1
            continue

        msgs = client.beta.threads.messages.list(thread_id=thread.id).data
        reply_text = None
        for msg in reversed(msgs):
            if msg.role == "assistant":
                content_list = msg.model_dump().get("content", [])
                if isinstance(content_list, list) and content_list:
                    txt_dict = content_list[0].get("text", {})
                    if isinstance(txt_dict, dict) and "value" in txt_dict:
                        reply_text = txt_dict["value"]
                        break

        if reply_text:
            try:
                topic_json = json.loads(reply_text)
                item["topic"] = topic_json.get("topic", "N/A")
            except:
                item["topic"] = reply_text.strip()[:200]
        else:
            item["topic"] = "N/A"

        success_count += 1
    except Exception as e:
        item["topic"] = "N/A"
        error_count += 1

    sleep(1)

with open(output_json, "w") as f:
    json.dump(data[:num_to_run], f, indent=2)

topics = [d.get("topic", "N/A") for d in data[:num_to_run]]
counter = Counter(topics)

print("\nClassification completed.")
print(f"Successfully classified: {success_count}")
print(f"Errors: {error_count}")
print(f"Output saved to: {output_json}\n")

print("Topic summary:")
for t, c in counter.items():
    print(f"{t}: {c}")
print(f"\nTotal unique topics: {len(counter)}")
print(f"N/A count: {counter.get('N/A', 0)}")
