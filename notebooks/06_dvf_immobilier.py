import requests
import pandas as pd
import psycopg2
import zipfile
import os
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

print("🔌 Connexion PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="sitescore", user="postgres",
    password="Khodia1571@"
)
cur = conn.cursor()
print("✅ Connexion OK !")

DEPS_IDF = ["75","77","78","91","92","93","94","95"]
os.makedirs("data/raw/dvf", exist_ok=True)
zip_path = "data/raw/dvf/dvf_2024.zip"

# ── Téléchargement ───────────────────────────
URL = "https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20260405-002306/valeursfoncieres-2024.txt.zip"

if not os.path.exists(zip_path):
    print("\n📥 Téléchargement DVF 2024...")
    r = requests.get(URL, stream=True, timeout=120)
    with open(zip_path, 'wb') as f:
        downloaded = 0
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            print(f"\r   {downloaded/1e6:.1f} Mo", end="")
    print(f"\n✅ Téléchargé : {os.path.getsize(zip_path)/1e6:.1f} Mo")
else:
    print("✅ Fichier déjà téléchargé !")

# ── Chargement par chunks ────────────────────
print("\n📂 Chargement par chunks...")
chunks = []

with zipfile.ZipFile(zip_path, 'r') as z:
    txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
    print(f"   Fichier : {txt_file}")
    with z.open(txt_file) as f:
        for chunk in pd.read_csv(
            f, sep="|", dtype=str,
            low_memory=False, encoding="utf-8",
            chunksize=50000
        ):
            if "Code departement" in chunk.columns:
                chunk = chunk[chunk["Code departement"].isin(DEPS_IDF)]
            chunks.append(chunk)
            print(f"\r   Chunks : {len(chunks)}", end="")

df = pd.concat(chunks, ignore_index=True)
print(f"\n✅ {len(df):,} transactions IDF chargées")
print(f"   Colonnes : {list(df.columns)[:8]}")

# ── Construction code INSEE ──────────────────
print("\n🔧 Construction code INSEE...")
col_dept    = "Code departement"
col_commune = "Code commune"
col_valeur  = "Valeur fonciere"
col_surface = "Surface reelle bati"

df["code_insee"] = df[col_dept].str.zfill(2) + df[col_commune].str.zfill(3)
print(f"   Exemple : {df['code_insee'].head(5).tolist()}")

# ── Calcul prix m² ───────────────────────────
print("\n💰 Calcul prix au m²...")
df[col_valeur]  = pd.to_numeric(df[col_valeur].str.replace(",","."), errors="coerce")
df[col_surface] = pd.to_numeric(df[col_surface].str.replace(",","."), errors="coerce")

df = df[
    (df[col_valeur]  > 10000) &
    (df[col_surface] > 20) &
    (df[col_valeur].notna()) &
    (df[col_surface].notna())
].copy()

df["prix_m2"] = (df[col_valeur] / df[col_surface]).round(0)
df = df[(df["prix_m2"] > 500) & (df["prix_m2"] < 50000)]
print(f"✅ {len(df):,} transactions valides")

# ── Agrégation par commune ───────────────────
df_prix = df.groupby("code_insee").agg(
    prix_m2_median=("prix_m2", "median"),
    prix_m2_moyen=("prix_m2",  "mean"),
    nb_transactions=("prix_m2", "count")
).reset_index()

df_prix["prix_m2_median"] = df_prix["prix_m2_median"].round(0)
df_prix["prix_m2_moyen"]  = df_prix["prix_m2_moyen"].round(0)

print(f"✅ {len(df_prix)} communes avec données DVF")
print(f"\n📊 Top 10 prix m² médian :")
for _, row in df_prix.nlargest(10, "prix_m2_median").iterrows():
    print(f"   {row['code_insee']} : {row['prix_m2_median']:,.0f} €/m²")

df_prix.to_csv("data/raw/dvf/prix_commune_idf.csv", index=False)
print("💾 CSV sauvegardé !")

# ── Jointure IRIS ────────────────────────────
print("\n🔗 Jointure DVF ↔ IRIS...")
cur.execute("""
    ALTER TABLE raw_data.iris
    ADD COLUMN IF NOT EXISTS prix_m2_median  FLOAT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS prix_m2_moyen   FLOAT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS nb_transactions INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS score_foncier   FLOAT DEFAULT 0;
""")
conn.commit()

updated = 0
for _, row in tqdm(df_prix.iterrows(), total=len(df_prix), desc="MAJ IRIS"):
    cur.execute("""
        UPDATE raw_data.iris
        SET prix_m2_median  = %s,
            prix_m2_moyen   = %s,
            nb_transactions = %s
        WHERE code_insee = %s;
    """, (float(row.prix_m2_median), float(row.prix_m2_moyen),
          int(row.nb_transactions), str(row.code_insee)))
    updated += cur.rowcount
conn.commit()
print(f"✅ {updated} IRIS mis à jour avec DVF !")

# ── Score foncier ────────────────────────────
cur.execute("""
    UPDATE raw_data.iris
    SET score_foncier = CASE
        WHEN prix_m2_median = 0 THEN 50
        ELSE LEAST(100, ROUND(
            (1 - (prix_m2_median::float /
            NULLIF((SELECT MAX(prix_m2_median)
                    FROM raw_data.iris
                    WHERE prix_m2_median > 0), 0))
            * 100)::numeric
        ))
    END;
""")
conn.commit()
print("✅ Score foncier calculé !")

# ── Recalcul SiteScore ───────────────────────
cur.execute("""
    UPDATE raw_data.iris
    SET sitescore = ROUND((
        score_revenu        * 0.22 +
        score_densite       * 0.18 +
        score_concurrence   * 0.22 +
        score_accessibilite * 0.18 +
        score_potentiel     * 0.10 +
        score_foncier       * 0.10
    )::numeric, 1);
""")
conn.commit()
print("✅ SiteScore recalculé avec DVF !")

# ── TOP 10 ───────────────────────────────────
cur.execute("""
    SELECT iris_code, nom_iris, commune, dept,
           sitescore, score_foncier,
           prix_m2_median, nb_concurrents_1km
    FROM raw_data.iris
    WHERE type_iris='H' AND prix_m2_median > 0
    ORDER BY sitescore DESC LIMIT 10;
""")
print(f"\n📊 TOP 10 SiteScore avec DVF :")
print(f"{'IRIS':<12} {'Quartier':<25} {'Commune':<20} {'Score':>6} {'Foncier':>8} {'Prix/m²':>8} {'Conc':>5}")
print("-" * 90)
for row in cur.fetchall():
    print(f"{row[0]:<12} {str(row[1])[:24]:<25} {str(row[2])[:19]:<20} "
          f"{row[4]:>6} {row[5]:>8} {row[6]:>8.0f}€ {row[7]:>5}")

cur.close()
conn.close()
print("\n🎉 DVF intégré dans SiteScore !")