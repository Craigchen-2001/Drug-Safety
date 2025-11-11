import pandas as pd  # type: ignore
import json

csv_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_journal.csv"
df = pd.read_csv(csv_path).fillna("N/A")

print("Total rows:", len(df))
print("Total unique PMIDs:", df["PMID"].nunique())
print("Columns:", df.columns.tolist())

choice = input("How many articles do you want to export? (Enter a number or 'all'): ")

if choice.lower() == "all":
    selected_pmids = df["PMID"].unique()
else:
    try:
        n = int(choice)
        selected_pmids = df["PMID"].unique()[:n]
    except:
        print("Invalid input, defaulting to 5")
        selected_pmids = df["PMID"].unique()[:5]

articles = []

for pmid, group in df.groupby("PMID"):
    if pmid not in selected_pmids:
        continue
    article = {
        "PMID": str(pmid),
        "PubMedPublicationYear": str(group["PubMedPublicationYear"].iloc[0]),
        "PubMedPublicationMonth": str(group["PubMedPublicationMonth"].iloc[0]),
        "Journals": []
    }
    for _, row in group.iterrows():
        journal = {
            "Journal_cleaned_1": str(row["Journal_cleaned_1"]),
            "Journal_cleaned_2": str(row["Journal_cleaned_2"]),
            "Journal_Proper": str(row["Journal_Proper"])
        }
        article["Journals"].append(journal)
    articles.append(article)

output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_journal.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Exported {len(articles)} articles to {output_path}")
