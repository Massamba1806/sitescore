import geopandas as gpd
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import requests
from tqdm import tqdm
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ── Connexion ────────────────────────────────
print("🔌 Connexion PostGIS...")
engine = create_engine(
    "postgresql+psycopg2://",
    creator=lambda: psycopg2.connect(
        host="127.0.0.1", port=5432,
        dbname="sitescore", user="postgres",
        password="Khodia1571@"
    )
)
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="sitescore", user="postgres",
    password="Khodia1571@"
)
cur = conn.cursor()
print("✅ Connexion OK !")

# ── Schémas ──────────────────────────────────
print("\n🔧 Création des schémas...")
cur.execute("""
    CREATE SCHEMA IF NOT EXISTS raw_data;
    CREATE SCHEMA IF NOT EXISTS features;
    CREATE SCHEMA IF NOT EXISTS scoring;
""")
conn.commit()
print("✅ Schémas créés !")

# ── Charge IRIS France ───────────────────────
print("\n📂 Chargement IRIS France...")
print("   (si tu n'as pas le fichier, télécharge-le depuis :")
print("   https://data.geopf.fr/telechargement)")

iris_path = "data/raw/iris/CONTOURS-IRIS.shp"

if not os.path.exists(iris_path):
    print(f"\n⚠️  Fichier non trouvé : {iris_path}")
    print("   Télécharge le shapefile IRIS et place-le dans data/raw/iris/")
    exit()

gdf_france = gpd.read_file(iris_path)
print(f"✅ {len(gdf_france)} IRIS France chargés")

# ── Filtre IDF ───────────────────────────────
CODES_DEP_IDF = ["75","77","78","91","92","93","94","95"]

print("\n🔍 Filtrage Île-de-France...")
gdf_idf = gdf_france[
    gdf_france["INSEE_COM"].str[:2].isin(CODES_DEP_IDF)
].copy()
print(f"✅ {len(gdf_idf)} IRIS IDF retenus")

# ── Reprojection WGS84 ───────────────────────
print("\n🔄 Reprojection WGS84...")
gdf_idf = gdf_idf.to_crs(epsg=4326)

# ── Renommage colonnes ───────────────────────
gdf_idf = gdf_idf.rename(columns={
    "CODE_IRIS": "iris_code",
    "NOM_IRIS":  "nom_iris",
    "INSEE_COM": "code_insee",
    "NOM_COM":   "commune",
    "TYP_IRIS":  "type_iris",
})

colonnes = ["iris_code","nom_iris","code_insee","commune","type_iris","geometry"]
colonnes_ok = [c for c in colonnes if c in gdf_idf.columns]
gdf_idf = gdf_idf[colonnes_ok]

# ── Calcul centroïdes ────────────────────────
print("\n📍 Calcul des centroïdes...")
gdf_proj = gdf_idf.to_crs(epsg=2154)
gdf_idf["centroid_lon"] = gdf_proj.centroid.to_crs(epsg=4326).x
gdf_idf["centroid_lat"] = gdf_proj.centroid.to_crs(epsg=4326).y
gdf_idf["surface_km2"]  = (gdf_proj.area / 1e6).round(3)
print("✅ Centroïdes calculés")

# ── Sauvegarde GeoJSON ───────────────────────
os.makedirs("data/exports", exist_ok=True)
gdf_idf.to_file("data/exports/iris_idf.geojson", driver="GeoJSON")
print(f"\n💾 GeoJSON sauvegardé : data/exports/iris_idf.geojson")

# ── Import PostGIS ───────────────────────────
print("\n📤 Import dans PostGIS...")
gdf_idf.to_postgis(
    name="iris",
    con=engine,
    schema="raw_data",
    if_exists="replace",
    index=False,
)
print(f"✅ {len(gdf_idf)} IRIS IDF importés dans raw_data.iris !")

# ── Stats ────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM raw_data.iris;")
print(f"✅ Vérification : {cur.fetchone()[0]} IRIS dans PostGIS")

cur.execute("""
    SELECT LEFT(code_insee,2) as dept, COUNT(*) as nb
    FROM raw_data.iris
    GROUP BY dept ORDER BY dept;
""")
print(f"\n📊 IRIS par département :")
for row in cur.fetchall():
    depts = {
        "75":"Paris","77":"Seine-et-Marne","78":"Yvelines",
        "91":"Essonne","92":"Hauts-de-Seine","93":"Seine-Saint-Denis",
        "94":"Val-de-Marne","95":"Val-d'Oise"
    }
    print(f"   {row[0]} {depts.get(row[0],'')} : {row[1]} IRIS")

cur.close()
conn.close()
print("\n🎉 Collecte IRIS IDF terminée !")