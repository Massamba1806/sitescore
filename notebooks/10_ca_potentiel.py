import psycopg2
import pandas as pd
import os

print("🔌 Connexion PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="sitescore", user="postgres",
    password="Khodia1571@"
)
cur = conn.cursor()
print("✅ Connexion OK !")

# ── Paramètres benchmark retail ──────────────
DEPENSE_ALIM_AN    = 5200   # € / ménage / an (INSEE 2024)
SURFACE_MOY        = 1200   # m² surface magasin standard

# Part de marché captée selon concurrence
def part_captee(nb_conc):
    if nb_conc == 0:   return 0.35
    elif nb_conc <= 2: return 0.22
    elif nb_conc <= 5: return 0.14
    elif nb_conc <= 10: return 0.08
    else:              return 0.05

print("\n💰 Calcul CA potentiel par IRIS...")

# Ajout colonnes
cur.execute("""
    ALTER TABLE raw_data.iris
    ADD COLUMN IF NOT EXISTS ca_potentiel_an    FLOAT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS ca_potentiel_m2    FLOAT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS part_marche_pct    FLOAT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS score_ca_potentiel FLOAT DEFAULT 0;
""")
conn.commit()

# Calcul
cur.execute("""
    SELECT iris_code, nb_menages, nb_concurrents_1km,
           nb_concurrents_500m, revenu_median
    FROM raw_data.iris
    WHERE type_iris = 'H' AND nb_menages > 0;
""")
rows = cur.fetchall()
print(f"   {len(rows)} IRIS à calculer...")

updated = 0
for row in rows:
    iris_code, nb_menages, nb_conc_1km, nb_conc_500m, revenu = row

    # Ajustement selon revenus
    if revenu and revenu > 35000:
        coeff_revenu = 1.15
    elif revenu and revenu > 25000:
        coeff_revenu = 1.0
    else:
        coeff_revenu = 0.88

    # Ajustement selon concurrence 500m (plus proche = plus impactant)
    if nb_conc_500m and nb_conc_500m > 0:
        malus_500m = 0.85
    else:
        malus_500m = 1.0

    part = part_captee(nb_conc_1km or 0)
    ca   = nb_menages * DEPENSE_ALIM_AN * part * coeff_revenu * malus_500m
    ca_m2 = ca / SURFACE_MOY

    cur.execute("""
        UPDATE raw_data.iris
        SET ca_potentiel_an    = %s,
            ca_potentiel_m2    = %s,
            part_marche_pct    = %s
        WHERE iris_code = %s;
    """, (round(ca), round(ca_m2), round(part*100, 1), iris_code))
    updated += 1

conn.commit()
print(f"✅ {updated} IRIS mis à jour !")

# Score CA normalisé
cur.execute("""
    UPDATE raw_data.iris
    SET score_ca_potentiel = LEAST(100, ROUND(
        (ca_potentiel_an::float /
        NULLIF((SELECT MAX(ca_potentiel_an)
                FROM raw_data.iris WHERE type_iris='H'), 0)
        * 100)::numeric
    ));
""")
conn.commit()

# Recalcul SiteScore avec CA
cur.execute("""
    UPDATE raw_data.iris
    SET sitescore = ROUND((
        score_revenu         * 0.20 +
        score_densite        * 0.15 +
        score_concurrence    * 0.20 +
        score_accessibilite  * 0.15 +
        score_ca_potentiel   * 0.15 +
        score_foncier        * 0.10 +
        score_potentiel      * 0.05
    )::numeric, 1);
""")
conn.commit()

# Recalcul score_final
cur.execute("""
    UPDATE raw_data.iris
    SET sitescore = ROUND((
        score_revenu         * 0.20 +
        score_densite        * 0.15 +
        score_concurrence    * 0.20 +
        score_accessibilite  * 0.15 +
        score_ca_potentiel   * 0.15 +
        score_foncier        * 0.10 +
        score_potentiel      * 0.05
    )::numeric, 1);
""")
conn.commit()
print("✅ SiteScore recalculé avec CA potentiel !")

# TOP 10
cur.execute("""
    SELECT iris_code, nom_iris, commune,
           sitescore, ca_potentiel_an,
           ca_potentiel_m2, part_marche_pct,
           nb_concurrents_1km, revenu_median
    FROM raw_data.iris
    WHERE type_iris='H' AND ca_potentiel_an > 0
    ORDER BY ca_potentiel_an DESC
    LIMIT 10;
""")
print(f"\n📊 TOP 10 IRIS par CA potentiel :")
print(f"{'Quartier':<30} {'Commune':<20} {'CA/an':>12} {'CA/m²':>8} {'Part%':>6} {'Conc':>5}")
print("-" * 85)
for row in cur.fetchall():
    print(f"{str(row[1])[:29]:<30} {str(row[2])[:19]:<20} "
          f"{row[4]:>12,.0f}€ {row[5]:>7,.0f}€ "
          f"{row[6]:>5.1f}% {row[7]:>5}")

cur.close()
conn.close()
print("\n🎉 CA potentiel calculé et intégré !")