import psycopg2
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import json
import os

print("🔌 Connexion PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="sitescore", user="postgres",
    password="Khodia1571@"
)
print("✅ OK !")

# ── Charge IRIS avec géométries ──────────────
print("\n📂 Chargement IRIS + géométries...")
from sqlalchemy import create_engine
engine = create_engine(
    "postgresql+psycopg2://",
    creator=lambda: psycopg2.connect(
        host="127.0.0.1", port=5432,
        dbname="sitescore", user="postgres",
        password="Khodia1571@"
    )
)

gdf = gpd.read_postgis("""
    SELECT
        iris_code, nom_iris, commune, dept,
        centroid_lon, centroid_lat,
        sitescore, nb_concurrents_500m,
        nb_concurrents_1km, ca_potentiel_an,
        revenu_median, densite_pop,
        score_concurrence, geometry
    FROM raw_data.iris
    WHERE type_iris = 'H'
    AND ca_potentiel_an > 0
    AND centroid_lon IS NOT NULL;
""", engine, geom_col="geometry")

gdf = gdf.to_crs(epsg=4326)
print(f"✅ {len(gdf)} IRIS chargés avec géométries")

# ── Classification ───────────────────────────
def classify(row):
    if (row.nb_concurrents_500m == 0 and
        row.nb_concurrents_1km <= 3 and
        row.ca_potentiel_an >= 500000 and
        row.densite_pop >= 500):
        return "desert"
    elif (row.nb_concurrents_1km <= 5 and
          row.ca_potentiel_an >= 800000 and
          row.densite_pop >= 1000):
        return "opportunite_forte"
    elif (row.nb_concurrents_1km <= 8 and
          row.ca_potentiel_an >= 400000):
        return "opportunite_moyenne"
    else:
        return "standard"

gdf["categorie"] = gdf.apply(classify, axis=1)

stats = gdf["categorie"].value_counts()
print(f"\n📊 Classification :")
for cat, n in stats.items():
    print(f"   {cat:<25} : {n}")

# ── Carte ────────────────────────────────────
print("\n🗺️  Génération carte pro...")

carte = folium.Map(
    location=[48.8566, 2.3522],
    zoom_start=10,
    tiles="CartoDB positron"
)

# Couleurs par catégorie
COLORS = {
    "desert":             {"fill":"#DC2626", "border":"#991B1B", "opacity":0.75},
    "opportunite_forte":  {"fill":"#F59E0B", "border":"#D97706", "opacity":0.60},
    "opportunite_moyenne":{"fill":"#3B82F6", "border":"#1D4ED8", "opacity":0.35},
    "standard":           {"fill":"#E5E7EB", "border":"#D1D5DB", "opacity":0.15},
}

LABELS = {
    "desert":             "🔴 Désert commercial",
    "opportunite_forte":  "🟡 Opportunité forte",
    "opportunite_moyenne":"🔵 Opportunité moyenne",
    "standard":           "⚪ Zone standard",
}

# ── Couche choroplèthe IRIS ──────────────────
for cat in ["standard","opportunite_moyenne","opportunite_forte","desert"]:
    subset = gdf[gdf["categorie"] == cat]
    if subset.empty:
        continue
    c = COLORS[cat]
    groupe = folium.FeatureGroup(name=LABELS[cat])

    for _, row in subset.iterrows():
        try:
            geoj = row.geometry.__geo_interface__
            popup_html = (
                f"<div style='font-family:Arial;width:220px;'>"
                f"<div style='background:#1A3557;color:white;padding:8px 12px;"
                f"border-radius:6px 6px 0 0;font-weight:bold;font-size:13px;'>"
                f"{LABELS[cat]}</div>"
                f"<div style='padding:10px 12px;background:#F8FAFF;'>"
                f"<b>{row['nom_iris']}</b><br>"
                f"<span style='color:#6B7280;font-size:11px;'>"
                f"{row['commune']} · Dept {row['dept']}</span><br><br>"
                f"💰 CA : <b>{row['ca_potentiel_an']:,.0f}€/an</b><br>"
                f"🏪 Concurrents 1km : <b>{row['nb_concurrents_1km']:.0f}</b><br>"
                f"👥 Densité : <b>{row['densite_pop']:,.0f}/km²</b><br>"
                f"💳 Revenu : <b>{row['revenu_median']:,.0f}€</b><br>"
                f"📊 SiteScore : <b>{row['sitescore']:.0f}/100</b>"
                f"</div></div>"
            )
            folium.GeoJson(
                geoj,
                style_function=lambda x,
                    fc=c["fill"],
                    bc=c["border"],
                    op=c["opacity"]: {
                    "fillColor":   fc,
                    "color":       bc,
                    "weight":      0.8,
                    "fillOpacity": op,
                },
                tooltip=f"{row['nom_iris']} · {row['commune']} · CA: {row['ca_potentiel_an']:,.0f}€",
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(groupe)
        except:
            continue

    groupe.add_to(carte)

# ── Marqueurs déserts avec CA ─────────────────
deserts = gdf[gdf["categorie"] == "desert"]
groupe_markers = folium.FeatureGroup(name="📍 Labels déserts")
for _, row in deserts.iterrows():
    ca_m = row['ca_potentiel_an'] / 1e6
    folium.Marker(
        location=[row.centroid_lat, row.centroid_lon],
        icon=folium.DivIcon(
            html=f"""
            <div style='background:#DC2626;color:white;padding:4px 8px;
                        border-radius:20px;font-size:10px;font-weight:700;
                        box-shadow:0 2px 6px rgba(0,0,0,0.3);
                        white-space:nowrap;border:2px solid white;'>
                🔴 {ca_m:.1f}M€
            </div>""",
            icon_size=(90, 28),
            icon_anchor=(45, 14)
        ),
        tooltip=f"🔴 {row['nom_iris']} · {row['commune']} · CA: {ca_m:.1f}M€/an"
    ).add_to(groupe_markers)
groupe_markers.add_to(carte)

# ── Opportunités fortes avec labels ──────────
opps = gdf[gdf["categorie"] == "opportunite_forte"].nlargest(20, "ca_potentiel_an")
groupe_opps = folium.FeatureGroup(name="⭐ Labels opportunités")
for _, row in opps.iterrows():
    ca_m = row['ca_potentiel_an'] / 1e6
    folium.Marker(
        location=[row.centroid_lat, row.centroid_lon],
        icon=folium.DivIcon(
            html=f"""
            <div style='background:#F59E0B;color:white;padding:3px 7px;
                        border-radius:20px;font-size:9px;font-weight:700;
                        box-shadow:0 2px 6px rgba(0,0,0,0.2);
                        white-space:nowrap;border:1.5px solid white;'>
                ⭐ {ca_m:.1f}M€
            </div>""",
            icon_size=(80, 24),
            icon_anchor=(40, 12)
        ),
        tooltip=f"⭐ {row['nom_iris']} · {row['commune']} · CA: {ca_m:.1f}M€/an"
    ).add_to(groupe_opps)
groupe_opps.add_to(carte)

folium.LayerControl(collapsed=False).add_to(carte)

# ── Légende pro ───────────────────────────────
legend = """
<div style="position:fixed;bottom:30px;left:30px;z-index:1000;
            background:white;padding:0;border-radius:12px;
            box-shadow:0 4px 20px rgba(0,0,0,0.15);
            font-family:'Helvetica Neue',Arial;overflow:hidden;
            min-width:260px;">
    <div style="background:#1A3557;color:white;padding:12px 16px;">
        <div style="font-size:13px;font-weight:700;letter-spacing:0.5px;">
            🗺️ DÉSERTS COMMERCIAUX IDF
        </div>
        <div style="font-size:10px;color:#93C5FD;margin-top:2px;">
            SiteScore · Massamba DIENG · 2026
        </div>
    </div>
    <div style="padding:12px 16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div style="width:16px;height:16px;border-radius:3px;
                        background:#DC2626;flex-shrink:0;"></div>
            <div>
                <div style="font-size:11px;font-weight:700;color:#1F2937;">
                    Désert commercial
                </div>
                <div style="font-size:10px;color:#6B7280;">
                    0 conc. 500m · ≤3 sur 1km · CA>500k€
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div style="width:16px;height:16px;border-radius:3px;
                        background:#F59E0B;flex-shrink:0;"></div>
            <div>
                <div style="font-size:11px;font-weight:700;color:#1F2937;">
                    Opportunité forte
                </div>
                <div style="font-size:10px;color:#6B7280;">
                    ≤5 conc. 1km · CA>800k€ · Den>1000/km²
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div style="width:16px;height:16px;border-radius:3px;
                        background:#3B82F6;flex-shrink:0;"></div>
            <div>
                <div style="font-size:11px;font-weight:700;color:#1F2937;">
                    Opportunité moyenne
                </div>
                <div style="font-size:10px;color:#6B7280;">
                    ≤8 conc. 1km · CA>400k€
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:16px;height:16px;border-radius:3px;
                        background:#E5E7EB;flex-shrink:0;"></div>
            <div>
                <div style="font-size:11px;font-weight:700;color:#1F2937;">
                    Zone standard
                </div>
                <div style="font-size:10px;color:#6B7280;">
                    Marché déjà couvert
                </div>
            </div>
        </div>
        <div style="margin-top:10px;padding-top:8px;border-top:1px solid #E5E7EB;
                    font-size:10px;color:#6B7280;">
            Cliquez sur une zone pour le détail complet
        </div>
    </div>
</div>
"""
carte.get_root().html.add_child(folium.Element(legend))

os.makedirs("data/exports", exist_ok=True)
output = "data/exports/carte_deserts_commerciaux_idf.html"
carte.save(output)
print(f"✅ Carte sauvegardée : {output}")
print("👉 Ouvre ce fichier dans ton navigateur !")

# Stats
print(f"\n📊 Stats finales :")
for cat in ["desert","opportunite_forte","opportunite_moyenne"]:
    subset = gdf[gdf["categorie"] == cat]
    if len(subset) > 0:
        print(f"\n   {LABELS[cat]} ({len(subset)} zones) :")
        top3 = subset.nlargest(3, "ca_potentiel_an")
        for _, row in top3.iterrows():
            print(f"      {row['commune']:<20} {row['nom_iris'][:25]:<25} "
                  f"CA: {row['ca_potentiel_an']:,.0f}€")

print("\n🎉 Carte pro générée !")