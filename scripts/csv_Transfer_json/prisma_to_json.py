import pandas as pd # type: ignore
import json

csv_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_prisma.csv"
df = pd.read_csv(csv_path).fillna("N/A")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))
print("Columns:", df.columns.tolist())

choice = input("How many records do you want to export? (Enter a number or 'all'): ")

if choice.lower() == "all":
    selected = df
else:
    try:
        n = int(choice)
        selected = df.head(n)
    except:
        print("Invalid input, defaulting to 5")
        selected = df.head(5)

records = []
for _, row in selected.iterrows():
    record = {col: str(row[col]) for col in df.columns}
    records.append(record)

output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_prisma.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Exported {len(records)} records to {output_path}")
