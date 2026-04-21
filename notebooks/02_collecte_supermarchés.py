import osmnx as ox
import geopandas as gpd
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

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

TAGS = {
    "shop": ["supermarket", "convenience", "grocery", "hypermarket"]
}

ENSEIGNES_CIBLES = [
    "lidl", "aldi", "carrefour", "carrefour market",
    "carrefour city", "intermarché", "super u", "monoprix",
    "franprix", "casino", "leclerc", "simply market",
    "bio c'bon", "naturalia", "g20"
]

print("\n🔍 Collecte supermarchés OSM en IDF...")
print("   (peut prendre 5-10 minutes...)")

try:
    gdf = ox.features_from_place(
        "Île-de-France, France",
        tags=TAGS
    )
    print(f"✅ {len(gdf)} commerces trouvés sur OSM")
except Exception as e:
    print(f"❌ Erreur OSM : {e}")
    exit()

print("\n🔧 Nettoyage des données...")
gdf = gdf[gdf.geometry.geom_type.isin(["Point","Polygon","MultiPolygon"])].copy()
gdf["geometry"] = gdf.geometry.apply(
    lambda g: g.centroid if g.geom_type in ["Polygon","MultiPolygon"] else g
)
gdf = gdf.set_crs(epsg=4326, allow_override=True)

cols_keep = []
for col in ["name","brand","operator","shop","addr:city","addr:postcode"]:
    if col in gdf.columns:
        cols_keep.append(col)

gdf = gdf[cols_keep + ["geometry"]].copy()
gdf = gdf.rename(columns={"addr:city": "ville", "addr:postcode": "code_postal"})

if "name" not in gdf.columns:
    gdf["name"] = "Inconnu"
gdf["name"] = gdf["name"].fillna("Inconnu")

if "brand" in gdf.columns:
    gdf["enseigne"] = gdf["brand"].str.lower().str.strip()
elif "name" in gdf.columns:
    gdf["enseigne"] = gdf["name"].str.lower().str.strip()
else:
    gdf["enseigne"] = "inconnu"

gdf["enseigne"] = gdf["enseigne"].fillna("inconnu")
gdf["est_cible"] = gdf["enseigne"].apply(
    lambda x: any(e in str(x) for e in ENSEIGNES_CIBLES)
)

print(f"✅ {len(gdf)} commerces après nettoyage")
print(f"   Enseignes cibles : {gdf['est_cible'].sum()}")

gdf["longitude"] = gdf.geometry.x
gdf["latitude"]  = gdf.geometry.y

print(f"\n📊 Top enseignes :")
top = gdf["enseigne"].value_counts().head(15)
for enseigne, nb in top.items():
    print(f"   {enseigne:<25} : {nb}")

os.makedirs("data/exports", exist_ok=True)
gdf.to_file("data/exports/supermarchés_idf.geojson", driver="GeoJSON")
print(f"\n💾 GeoJSON sauvegardé !")

print("\n📤 Import dans PostGIS...")
gdf_import = gdf.reset_index(drop=True)
gdf_import.columns = [c.replace(":","_").replace(" ","_").lower()
                      for c in gdf_import.columns]

gdf_import.to_postgis(
    name="supermarchés",
    con=engine,
    schema="raw_data",
    if_exists="replace",
    index=False,
)

cur.execute('SELECT COUNT(*) FROM raw_data."supermarchés";')
print(f"✅ {cur.fetchone()[0]} commerces importés dans PostGIS !")

cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_supermarchés_geom
    ON raw_data."supermarchés" USING GIST(geometry);
""")
conn.commit()
print("✅ Index spatial créé !")

cur.close()
conn.close()
print("\n🎉 Collecte supermarchés IDF terminée !")