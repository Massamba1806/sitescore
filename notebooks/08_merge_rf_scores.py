import pandas as pd
import os

print("📂 Fusion SiteScore + RF scores...")

df_site = pd.read_csv("data/exports/sitescore_idf.csv")
df_rf   = pd.read_csv("data/exports/rf_scores.csv")

# Supprime colonnes dupliquées avant merge
cols_to_drop = [c for c in df_site.columns if c.endswith('.1')]
df_site = df_site.drop(columns=cols_to_drop)

# Garde une seule version de ca_potentiel
for col in ["ca_potentiel_an", "ca_potentiel_m2", "part_marche_pct"]:
    dupes = [c for c in df_site.columns if c.startswith(col)]
    if len(dupes) > 1:
        df_site = df_site.drop(columns=dupes[1:])

df = df_site.merge(df_rf, on="iris_code", how="left")
df["rf_score"] = df["rf_score"].fillna(0)

# Score final combiné
df["score_final"] = (
    df["sitescore"] * 0.5 +
    df["rf_score"]  * 0.5
).round(1)

df.to_csv("data/exports/sitescore_idf.csv", index=False)
print(f"✅ {len(df)} IRIS mis à jour")
print(f"   Colonnes : {list(df.columns)}")
print(f"\n📊 TOP 10 score final :")
top = df.nlargest(10, "score_final")[
    ["nom_iris","commune","sitescore","rf_score","score_final","ca_potentiel_an"]
]
for _, row in top.iterrows():
    print(f"   {row.commune:<20} {row.nom_iris[:25]:<25} "
          f"Site:{row.sitescore:.0f} RF:{row.rf_score:.0f} "
          f"Final:{row.score_final:.0f} "
          f"CA:{row.ca_potentiel_an:,.0f}€")