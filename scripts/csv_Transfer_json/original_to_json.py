import pandas as pd
import json

csv_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_original.csv"
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

for _, row in df.iterrows():
    if row["PMID"] not in selected_pmids:
        continue

    article = {
        "PMID": str(row["PMID"]),
        "Title": str(row["Title"]),
        "Abstract": str(row["Abstract"]),
        "Language": str(row["Language"]),
        "Journal": str(row["Journal"]),
        "PublicationYear": str(row["PublicationYear"]),
        "PublicationMonth": str(row["PublicationMonth"]),
        "PubMedPublicationYear": str(row["PubMedPublicationYear"]),
        "PubMedPublicationMonth": str(row["PubMedPublicationMonth"]),
        "Volume": str(row["Volume"]),
        "Issue": str(row["Issue"]),
        "ISSN": str(row["ISSN"]),
        "ISOAbbreviation": str(row["ISOAbbreviation"]),
        "MedlineCountry": str(row["MedlineCountry"]),
        "MedlineTA": str(row["MedlineTA"]),
        "NlmUniqueID": str(row["NlmUniqueID"]),
        "ISSNLinking": str(row["ISSNLinking"]),
        "Authors": [],
        "MeshTerms": [],
        "PublicationTypes": []
    }

    for i in range(1, 24):
        author_col = f"Author{i}"
        affil_col = f"Affiliation{i}"
        if author_col in df.columns and str(row[author_col]) != "N/A":
            article["Authors"].append({
                "Name": str(row[author_col]),
                "Affiliation": str(row[affil_col]) if affil_col in df.columns else "N/A"
            })

    for i in range(1, 24):
        mesh_col = f"MeshTerm{i}"
        if mesh_col in df.columns and str(row[mesh_col]) != "N/A":
            article["MeshTerms"].append(str(row[mesh_col]))

    for i in range(1, 5):
        pub_col = f"PublicationType{i}"
        if pub_col in df.columns and str(row[pub_col]) != "N/A":
            article["PublicationTypes"].append(str(row[pub_col]))

    articles.append(article)

output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_original.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Exported {len(articles)} articles to {output_path}")
