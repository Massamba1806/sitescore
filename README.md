# 🎯 SiteScore — Moteur de recommandation d'implantation commerciale IDF

> **Tu entres une commune — SiteScore analyse 5 264 zones et te dit où ouvrir.**  
> Score hybride : **règles expertes + Random Forest (68% accuracy)**

[![Streamlit App](https://img.shields.io/badge/Dashboard-Live-brightgreen?style=for-the-badge&logo=streamlit)](https://sitescore-q6i7bsnc7grykdgyg4mdud.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Code-blue?style=for-the-badge&logo=github)](https://github.com/Massamba1806/sitescore)

---

## 🎯 Problématique

Où ouvrir le prochain supermarché en Île-de-France ?  
SiteScore répond automatiquement en croisant **5 sources de données** et un **modèle Machine Learning** entraîné sur les implantations existantes.

---

## 📊 Résultats clés

| Métrique | Valeur |
|---|---|
| IRIS analysés | **5 264** |
| Communes IDF couvertes | **351** |
| Supermarchés concurrents OSM | **7 259** |
| Random Forest accuracy | **68%** |
| Features scoring | **6** |
| Export PDF automatique | ✅ |
| Comparaison multi-communes | ✅ |
| Déserts commerciaux IDF | ✅ |

---

## 🏗️ Architecture technique
---

## 🧮 Formule de scoring
---

## 💰 CA Potentiel estimé

```python
CA estimé = nb_ménages × 5200€/an × part_captée × coeff_revenu
# part_captée : 35% (0 concurrent) → 5% (10+ concurrents)
```

---

## 🗺️ Déserts commerciaux IDF

Carte interactive des zones avec :
- **Fort potentiel CA** (>500k€/an)
- **Peu de concurrence** (0 concurrent dans 500m)
- **Bonne densité** (>500 hab/km²)

---

## 🛠️ Stack technique

| Catégorie | Outils |
|---|---|
| **Langage** | Python 3.13 |
| **Spatial** | GeoPandas · PostGIS · PostgreSQL |
| **Machine Learning** | Random Forest · Scikit-learn |
| **Données** | IGN IRIS · INSEE · OSM · DVF 2024 |
| **Dashboard** | Streamlit · Plotly · Folium |
| **PDF** | ReportLab |
| **Déploiement** | Streamlit Cloud |

---

## 🚀 Installation

```bash
git clone https://github.com/Massamba1806/sitescore
cd sitescore
pip install -r requirements.txt
streamlit run app/dashboard.py
```

**Prérequis :** PostgreSQL + PostGIS installés localement.

---

## 📱 Fonctionnalités dashboard

| Mode | Description |
|---|---|
| 🔍 Analyse commune | TOP 5 emplacements + carte + scores + PDF |
| 📊 Comparaison | Radar multi-critères entre communes |
| 🗺️ Déserts IDF | Carte des opportunités d'implantation |

---

## 👤 Auteur

**Massamba DIENG** — Chargé d'études Géomarketing  
Master Géomarketing · UPEC · 2 ans chez ALDI (71 PDV IDF)

🌐 [Portfolio](https://massamba1806.github.io) · 
💼 [LinkedIn](https://linkedin.com/in/massamba-dieng-287526271) · 
🐙 [GitHub](https://github.com/Massamba1806)

---

*Sources : IGN IRIS 2024 · INSEE FILOSOF · OpenStreetMap · DVF data.gouv.fr · API BAN*
