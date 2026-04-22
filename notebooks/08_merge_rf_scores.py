import pandas as pd
import os

print("📂 Fusion SiteScore + RF scores...")

df_site = pd.read_csv("data/exports/sitescore_idf.csv")
df_rf   = pd.read_csv("data/exports/rf_scores.csv")

df = df_site.merge(df_rf, on="iris_code", how="left")
df["rf_score"] = df["rf_score"].fillna(0)

# Score combiné
df["score_final"] = (
    df["sitescore"] * 0.5 +
    df["rf_score"]  * 0.5
).round(1)

df.to_csv("data/exports/sitescore_idf.csv", index=False)
print(f"✅ {len(df)} IRIS mis à jour")
print(f"   Colonnes : {list(df.columns)}")
print(f"\n📊 TOP 10 score final :")
top = df.nlargest(10, "score_final")[
    ["nom_iris","commune","sitescore","rf_score","score_final"]
]
for _, row in top.iterrows():
    print(f"   {row.commune:<20} {row.nom_iris[:25]:<25} "
          f"Site:{row.sitescore:.0f} RF:{row.rf_score:.0f} "
          f"Final:{row.score_final:.0f}")