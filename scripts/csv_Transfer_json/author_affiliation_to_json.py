import pandas as pd
import json

df = pd.read_csv("/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_author_affiliation.csv").fillna("N/A")

articles = []

for pmid, group in df.groupby("PMID"):
    article = {
        "PMID": str(pmid),
        "Title": str(group["Title"].iloc[0]),
        "Abstract": str(group["Abstract"].iloc[0]),
        "PubMedPublicationYear": str(group["PubMedPublicationYear"].iloc[0]),
        "PubMedPublicationMonth": str(group["PubMedPublicationMonth"].iloc[0]),
        "Journal": str(group["Journal"].iloc[0]),
        "Authors": []
    }
    for _, row in group.iterrows():
        author = {
            "AuthorNum": str(row["AuthorNum"]),
            "Author": str(row["Author"]),
            "AffiliationNum": str(row["AffiliationNum"]),
            "Affiliation": str(row["Affiliation"]),
            "Institution": str(row["Institution"]),
            "State": str(row["State"]),
            "Country": str(row["Country"]),
            "Label": str(row["Label"]),
            "State_Proper": str(row["State_Proper"]),
            "Country_Proper": str(row["Country_Proper"]),
            "Label_2": str(row["Label_2"]),
            "Last_Name_First": str(row["Last_Name_First"])
        }
        article["Authors"].append(author)
    articles.append(article)

output_path = "/Users/chenweichi/Desktop/Drug_Safety_Project/data/raw/maude_author_affiliationdebug.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Exported {len(articles)} articles to {output_path}")
