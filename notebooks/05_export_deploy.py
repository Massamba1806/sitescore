import psycopg2
import pandas as pd
import os

print("🔌 Connexion PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="sitescore", user="postgres",
    password="Khodia1571@"
)

print("📤 Export données pour déploiement...")
df = pd.read_sql("""
    SELECT iris_code, nom_iris, commune, dept,
           type_iris, centroid_lon, centroid_lat,
           sitescore, score_concurrence, score_revenu,
           score_densite, score_accessibilite, score_potentiel,
           nb_concurrents_500m, nb_concurrents_1km, nb_concurrents_2km,
           revenu_median, densite_pop, pop_totale, potentiel_ca
    FROM raw_data.iris
    WHERE type_iris = 'H'
    AND sitescore > 0
    AND centroid_lon IS NOT NULL;
""", conn)

conn.close()

os.makedirs("data/exports", exist_ok=True)
df.to_csv("data/exports/sitescore_idf.csv", index=False)
print(f"✅ {len(df)} IRIS exportés → data/exports/sitescore_idf.csv")
print(f"   Taille : {os.path.getsize('data/exports/sitescore_idf.csv')/1e6:.1f} Mo")