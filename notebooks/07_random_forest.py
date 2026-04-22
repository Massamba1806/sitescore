import psycopg2
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

print("🔌 Connexion PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="sitescore", user="postgres",
    password="Khodia1571@"
)
print("✅ Connexion OK !")

# ── Charge les données ───────────────────────
print("\n📂 Chargement des données...")
df = pd.read_sql("""
    SELECT
        i.iris_code,
        i.nom_iris,
        i.commune,
        i.dept,
        i.revenu_median,
        i.densite_pop,
        i.pop_totale,
        i.nb_menages,
        i.tx_chomage,
        i.part_jeunes,
        i.nb_concurrents_500m,
        i.nb_concurrents_1km,
        i.nb_concurrents_2km,
        i.score_accessibilite,
        i.potentiel_ca,
        i.prix_m2_median,
        i.surface_km2,
        i.sitescore,
        CASE WHEN s.nb_supers > 0 THEN 1 ELSE 0 END as a_supermarche
    FROM raw_data.iris i
    LEFT JOIN (
        SELECT iris_code, COUNT(*) as nb_supers
        FROM (
            SELECT i2.iris_code
            FROM raw_data.iris i2
            JOIN raw_data."supermarchés" s2
            ON ST_Within(s2.geometry, i2.geometry)
        ) sub
        GROUP BY iris_code
    ) s ON i.iris_code = s.iris_code
    WHERE i.type_iris = 'H'
    AND i.revenu_median > 0
    AND i.densite_pop > 0;
""", conn)
conn.close()

print(f"✅ {len(df)} IRIS chargés")
print(f"   Avec supermarché  : {df['a_supermarche'].sum()}")
print(f"   Sans supermarché  : {(df['a_supermarche']==0).sum()}")

# ── Features ─────────────────────────────────
FEATURES = [
    "revenu_median",
    "densite_pop",
    "pop_totale",
    "nb_menages",
    "tx_chomage",
    "part_jeunes",
    "nb_concurrents_1km",
    "nb_concurrents_2km",
    "score_accessibilite",
    "potentiel_ca",
    "prix_m2_median",
    "surface_km2",
]

df_clean = df[FEATURES + ["a_supermarche", "iris_code"]].dropna()
print(f"\n✅ {len(df_clean)} IRIS après nettoyage")

X = df_clean[FEATURES].values
y = df_clean["a_supermarche"].values

# ── Split train/test ──────────────────────────
print("\n🔀 Split train/test (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train : {len(X_train)} | Test : {len(X_test)}")

# ── Normalisation ─────────────────────────────
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

# ── Random Forest ─────────────────────────────
print("\n🤖 Entraînement Random Forest...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train_s, y_train)
print("✅ Modèle entraîné !")

# ── Évaluation ────────────────────────────────
print("\n📊 Évaluation du modèle...")
y_pred = rf.predict(X_test_s)
accuracy = (y_pred == y_test).mean()
print(f"   Accuracy : {accuracy:.3f}")

cv_scores = cross_val_score(rf, X_train_s, y_train, cv=5)
print(f"   Cross-val (5-fold) : {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

print(f"\n📊 Rapport de classification :")
print(classification_report(y_test, y_pred,
      target_names=["Sans supermarché", "Avec supermarché"]))

# ── Feature importance ────────────────────────
print(f"\n📊 Importance des features :")
importances = pd.DataFrame({
    "feature":    FEATURES,
    "importance": rf.feature_importances_
}).sort_values("importance", ascending=False)

for _, row in importances.iterrows():
    bar = "█" * int(row.importance * 50)
    print(f"   {row.feature:<25} {bar} {row.importance:.3f}")

# ── Score RF pour chaque IRIS ─────────────────
print(f"\n🏆 Calcul score RF pour tous les IRIS...")
X_all_s = scaler.transform(df_clean[FEATURES].values)
proba   = rf.predict_proba(X_all_s)[:, 1]

df_clean = df_clean.copy()
df_clean["rf_score"] = (proba * 100).round(1)

print(f"\n📊 TOP 15 IRIS par score RF :")
top15 = df_clean.nlargest(15, "rf_score")[
    ["iris_code", "rf_score", "nb_concurrents_1km",
     "revenu_median", "densite_pop"]
]
for _, row in top15.iterrows():
    print(f"   {row.iris_code} — RF: {row.rf_score:.0f} "
          f"| Conc: {row.nb_concurrents_1km:.0f} "
          f"| Rev: {row.revenu_median:.0f}€ "
          f"| Den: {row.densite_pop:.0f}")

# ── Sauvegarde modèle ─────────────────────────
os.makedirs("data/exports", exist_ok=True)
with open("data/exports/rf_model.pkl", "wb") as f:
    pickle.dump(rf, f)
with open("data/exports/rf_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("data/exports/rf_features.pkl", "wb") as f:
    pickle.dump(FEATURES, f)

print(f"\n💾 Modèle sauvegardé : data/exports/rf_model.pkl")

# ── Sauvegarde scores RF dans CSV ────────────
df_rf = df_clean[["iris_code", "rf_score"]].copy()
df_rf.to_csv("data/exports/rf_scores.csv", index=False)
print(f"💾 Scores RF sauvegardés : data/exports/rf_scores.csv")

print("\n🎉 Random Forest terminé !")