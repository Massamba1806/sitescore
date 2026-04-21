import psycopg2
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

# ── Vérifie que la concurrence est déjà calculée ──
cur.execute("""
    SELECT COUNT(*) FROM raw_data.iris
    WHERE nb_concurrents_1km > 0;
""")
nb = cur.fetchone()[0]
print(f"✅ Concurrence déjà calculée pour {nb} IRIS — on passe directement aux scores !")

# ── Scores en une seule requête ──────────────
print("\n🏆 Calcul des scores...")
cur.execute("""
    UPDATE raw_data.iris SET
    score_concurrence = CASE
        WHEN nb_concurrents_500m = 0 AND nb_concurrents_1km = 0 THEN 100
        WHEN nb_concurrents_500m = 0 AND nb_concurrents_1km <= 2 THEN 80
        WHEN nb_concurrents_500m = 0 AND nb_concurrents_1km <= 5 THEN 60
        WHEN nb_concurrents_500m <= 1 THEN 40
        WHEN nb_concurrents_500m <= 3 THEN 20
        ELSE 10
    END,
    score_accessibilite = CASE
        WHEN type_iris = 'H' AND densite_pop > 10000 THEN 95
        WHEN type_iris = 'H' AND densite_pop > 5000  THEN 80
        WHEN type_iris = 'H' AND densite_pop > 2000  THEN 65
        WHEN type_iris = 'H' AND densite_pop > 500   THEN 50
        WHEN type_iris = 'A' THEN 30
        ELSE 40
    END,
    potentiel_ca = ROUND((nb_menages * 5000 * 0.35)::numeric),
    score_revenu = LEAST(100, ROUND(
        (revenu_median::float /
        NULLIF((SELECT MAX(revenu_median) FROM raw_data.iris), 0)
        * 100)::numeric
    )),
    score_densite = LEAST(100, ROUND(
        (densite_pop::float /
        NULLIF((SELECT MAX(densite_pop) FROM raw_data.iris), 0)
        * 100)::numeric
    ));
""")
conn.commit()
print("✅ Scores intermédiaires calculés !")

cur.execute("""
    UPDATE raw_data.iris
    SET score_potentiel = LEAST(100, ROUND(
        (potentiel_ca /
        NULLIF((SELECT MAX(potentiel_ca) FROM raw_data.iris), 0)
        * 100)::numeric
    ));
""")
conn.commit()

cur.execute("""
    UPDATE raw_data.iris
    SET sitescore = ROUND((
        score_revenu        * 0.25 +
        score_densite       * 0.20 +
        score_concurrence   * 0.25 +
        score_accessibilite * 0.20 +
        score_potentiel     * 0.10
    )::numeric, 1);
""")
conn.commit()
print("✅ Score global SiteScore calculé !")

# ── TOP 20 ───────────────────────────────────
print("\n📊 TOP 20 IRIS meilleur SiteScore :")
cur.execute("""
    SELECT iris_code, nom_iris, commune, dept,
           sitescore, score_concurrence,
           score_revenu, score_densite,
           nb_concurrents_1km
    FROM raw_data.iris
    WHERE type_iris = 'H'
    ORDER BY sitescore DESC
    LIMIT 20;
""")
print(f"\n{'IRIS':<12} {'Quartier':<25} {'Commune':<20} {'Score':>6} {'Conc':>5} {'Rev':>5} {'Den':>5} {'Nb conc 1km':>11}")
print("-" * 100)
for row in cur.fetchall():
    print(f"{row[0]:<12} {str(row[1])[:24]:<25} {str(row[2])[:19]:<20} "
          f"{row[4]:>6} {row[5]:>5} {row[6]:>5} {row[7]:>5} {row[8]:>11}")

cur.execute("""
    SELECT ROUND(AVG(sitescore)::numeric,1),
           ROUND(MAX(sitescore)::numeric,1),
           ROUND(MIN(sitescore)::numeric,1),
           COUNT(*)
    FROM raw_data.iris WHERE type_iris = 'H';
""")
stats = cur.fetchone()
print(f"\n📊 Stats : moy={stats[0]} max={stats[1]} min={stats[2]} total={stats[3]}")

cur.close()
conn.close()
print("\n🎉 Feature engineering terminé !")