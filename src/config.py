import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     "5432",
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

DB_URL = (
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@127.0.0.1:5432/{DB_CONFIG['dbname']}"
)

ORS_API_KEY = os.getenv("ORS_API_KEY")
ENSEIGNE    = os.getenv("ENSEIGNE", "supermarche")
ZONE        = os.getenv("ZONE", "idf")

# ── Paramètres IDF ───────────────────────────
IDF_BBOX = {
    "min_lon": 1.446,
    "max_lon": 3.560,
    "min_lat": 48.120,
    "max_lat": 49.241,
}

CODES_DEP_IDF = [
    "75", "77", "78", "91",
    "92", "93", "94", "95"
]

# ── Poids du scoring ─────────────────────────
WEIGHTS = {
    "revenu_median":      0.25,
    "densite_pop":        0.20,
    "score_concurrence":  0.25,
    "accessibilite":      0.20,
    "potentiel_ca":       0.10,
}

SRID = 4326