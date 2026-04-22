import streamlit as st
import psycopg2
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
# ── SESSION STATE ────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "splash"

# ── SPLASH PAGE ───────────────────────────────
if st.session_state.page == "splash":
    st.markdown("""
        <div style='min-height:100vh; background:#0A0E1A;
                    display:flex; flex-direction:column;
                    align-items:center; justify-content:center;
                    text-align:center; padding:40px;'>
            <div style='font-size:11px; color:#4A5568; letter-spacing:4px;
                        text-transform:uppercase; margin-bottom:20px;'>
                RETAIL LOCATION INTELLIGENCE · ÎLE-DE-FRANCE
            </div>
            <div style='font-size:72px; font-weight:900; line-height:1;
                        margin-bottom:8px;'>
                <span style='color:#00D4FF;'>SITE</span>
                <span style='color:#E0E6ED;'>SCORE</span>
            </div>
            <div style='width:60px; height:3px;
                        background:linear-gradient(90deg,#00D4FF,#00FF88);
                        margin:20px auto;'></div>
            <div style='font-size:13px; color:#4A5568; letter-spacing:3px;
                        text-transform:uppercase; margin-bottom:48px;'>
                MOTEUR D'IMPLANTATION COMMERCIALE
            </div>
            <div style='display:flex; gap:48px; margin-bottom:56px;
                        flex-wrap:wrap; justify-content:center;'>
                <div style='text-align:center;'>
                    <div style='font-size:40px; font-weight:900; color:#00D4FF;'>351</div>
                    <div style='font-size:10px; color:#4A5568; letter-spacing:2px;
                                text-transform:uppercase;'>Communes</div>
                </div>
                <div style='width:1px; background:#1E2D3D;'></div>
                <div style='text-align:center;'>
                    <div style='font-size:40px; font-weight:900; color:#00FF88;'>5 264</div>
                    <div style='font-size:10px; color:#4A5568; letter-spacing:2px;
                                text-transform:uppercase;'>IRIS analysés</div>
                </div>
                <div style='width:1px; background:#1E2D3D;'></div>
                <div style='text-align:center;'>
                    <div style='font-size:40px; font-weight:900; color:#FFD700;'>7 259</div>
                    <div style='font-size:10px; color:#4A5568; letter-spacing:2px;
                                text-transform:uppercase;'>Supermarchés</div>
                </div>
                <div style='width:1px; background:#1E2D3D;'></div>
                <div style='text-align:center;'>
                    <div style='font-size:40px; font-weight:900; color:#C084FC;'>5</div>
                    <div style='font-size:10px; color:#4A5568; letter-spacing:2px;
                                text-transform:uppercase;'>Features ML</div>
                </div>
            </div>
            <div style='border:1px solid #1E2D3D; border-radius:16px;
                        padding:24px 40px; margin-bottom:48px;
                        background:#0D1117;'>
                <div style='font-size:10px; color:#4A5568; letter-spacing:3px;
                            text-transform:uppercase; margin-bottom:12px;'>
                    RÉALISÉ PAR
                </div>
                <div style='font-size:28px; font-weight:900; color:#E0E6ED;
                            letter-spacing:3px;'>
                    Massamba <span style='color:#00D4FF;'>DIENG</span>
                </div>
                <div style='font-size:11px; color:#4A5568; margin-top:6px;
                            letter-spacing:2px; text-transform:uppercase;'>
                    Chargé d'études Géomarketing · Master UPEC
                </div>
                <div style='display:flex; gap:16px; justify-content:center;
                            margin-top:16px; flex-wrap:wrap;'>
                    <span style='font-size:10px; color:#00D4FF; background:#00D4FF11;
                                 padding:4px 12px; border-radius:20px;
                                 border:1px solid #00D4FF33;'>Python</span>
                    <span style='font-size:10px; color:#00FF88; background:#00FF8811;
                                 padding:4px 12px; border-radius:20px;
                                 border:1px solid #00FF8833;'>PostGIS</span>
                    <span style='font-size:10px; color:#FFD700; background:#FFD70011;
                                 padding:4px 12px; border-radius:20px;
                                 border:1px solid #FFD70033;'>QGIS</span>
                    <span style='font-size:10px; color:#C084FC; background:#C084FC11;
                                 padding:4px 12px; border-radius:20px;
                                 border:1px solid #C084FC33;'>Streamlit</span>
                    <span style='font-size:10px; color:#FF6B35; background:#FF6B3511;
                                 padding:4px 12px; border-radius:20px;
                                 border:1px solid #FF6B3533;'>OSM</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("⚡  LAUNCH PLATFORM", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    st.stop()
st.set_page_config(
    page_title="SiteScore Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* DARK MODE COMPLET */
    .stApp { background-color: #0A0E1A; }
    .main { background-color: #0A0E1A; }
    [data-testid="stSidebar"] {
        background: #0D1117;
        border-right: 1px solid #1E2D3D;
    }
    [data-testid="stSidebar"] * { color: #E0E6ED !important; }

    /* TYPOGRAPHY */
    * { font-family: 'Inter', 'SF Pro Display', sans-serif; }
    h1,h2,h3 { color: #E0E6ED !important; }
    p, span, div { color: #8B9BB4; }

    /* SELECTBOX & SLIDER */
    .stSelectbox > div > div {
        background: #0D1117 !important;
        border: 1px solid #1E2D3D !important;
        color: #E0E6ED !important;
    }
    .stSlider > div > div { background: #1E2D3D !important; }

    /* METRIC CARDS */
    .kpi-card {
        background: linear-gradient(135deg, #0D1117, #111827);
        border: 1px solid #1E2D3D;
        border-radius: 12px;
        padding: 20px 24px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: var(--accent);
    }
    .kpi-value {
        font-size: 36px;
        font-weight: 800;
        color: var(--accent) !important;
        line-height: 1;
        margin: 0;
    }
    .kpi-label {
        font-size: 10px;
        color: #4A5568 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 6px 0 0;
    }
    .kpi-delta {
        font-size: 11px;
        margin-top: 4px;
    }

    /* RANK CARDS */
    .rank-card {
        background: #0D1117;
        border: 1px solid #1E2D3D;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s;
    }
    .rank-card:hover { border-color: #2E4A6B; }
    .rank-card::after {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: var(--rank-color);
    }
    .rank-num {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .rank-name {
        font-size: 16px;
        font-weight: 700;
        color: #E0E6ED !important;
        margin: 4px 0 2px;
    }
    .rank-commune {
        font-size: 12px;
        color: #4A5568 !important;
    }
    .rank-score {
        font-size: 40px;
        font-weight: 900;
        line-height: 1;
    }
    .score-bar-bg {
        background: #1E2D3D;
        border-radius: 4px;
        height: 4px;
        margin-top: 12px;
    }
    .score-bar-fill {
        height: 4px;
        border-radius: 4px;
        background: var(--rank-color);
    }
    .tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 600;
        margin: 2px;
        letter-spacing: 0.5px;
    }

    /* SECTION HEADERS */
    .sec-header {
        font-size: 10px;
        font-weight: 700;
        color: #4A5568 !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1E2D3D;
    }

    /* TABLE */
    .stDataFrame { background: #0D1117 !important; }
    .stDataFrame td, .stDataFrame th {
        background: #0D1117 !important;
        color: #8B9BB4 !important;
        border-color: #1E2D3D !important;
    }

    /* HIDE STREAMLIT BRANDING */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; }

    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #0A0E1A; }
    ::-webkit-scrollbar-thumb { background: #1E2D3D; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Couleurs ──────────────────────────────────
RANK_COLORS = ["#00D4FF", "#00FF88", "#FFD700", "#FF6B35", "#C084FC"]
RANK_LABELS = ["OPTIMAL", "EXCELLENT", "BON", "CORRECT", "ACCEPTABLE"]

# ── Connexion ─────────────────────────────────
import os

DATA_PATH = "data/exports/sitescore_idf.csv"

@st.cache_data
def load_csv():
    return pd.read_csv(DATA_PATH)

@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host="127.0.0.1", port=5432,
        dbname="sitescore", user="postgres",
        password="Khodia1571@"
    )

@st.cache_data
def get_communes():
    if os.path.exists(DATA_PATH):
        df = load_csv()
        return df[["commune","dept"]].drop_duplicates().sort_values("commune")
    conn = get_conn()
    return pd.read_sql("""
        SELECT DISTINCT commune, dept FROM raw_data.iris
        WHERE type_iris='H' AND commune IS NOT NULL
        ORDER BY commune;
    """, conn)

@st.cache_data
def get_top5(commune):
    if os.path.exists(DATA_PATH):
        df = load_csv()
        result = df[df["commune"].str.contains(commune, case=False, na=False)]
        return result.nlargest(5, "sitescore")
    conn = get_conn()
    return pd.read_sql(f"""
        SELECT * FROM raw_data.iris
        WHERE commune ILIKE '%{commune}%'
        AND type_iris='H' AND sitescore > 0
        ORDER BY sitescore DESC LIMIT 5;
    """, conn)

@st.cache_data
def get_all(commune):
    if os.path.exists(DATA_PATH):
        df = load_csv()
        return df[df["commune"].str.contains(commune, case=False, na=False)].sort_values("sitescore", ascending=False)
    conn = get_conn()
    return pd.read_sql(f"""
        SELECT * FROM raw_data.iris
        WHERE commune ILIKE '%{commune}%'
        AND type_iris='H' AND sitescore > 0
        ORDER BY sitescore DESC;
    """, conn)

@st.cache_data
def get_idf_stats():
    if os.path.exists(DATA_PATH):
        df = load_csv()
        return pd.Series({
            "nb_communes": df["commune"].nunique(),
            "nb_iris":     len(df),
            "score_moy":   round(df["sitescore"].mean(), 1),
            "score_max":   round(df["sitescore"].max(), 1),
        })
    conn = get_conn()
    return pd.read_sql("""
        SELECT COUNT(DISTINCT commune) as nb_communes,
               COUNT(*) as nb_iris,
               ROUND(AVG(sitescore)::numeric,1) as score_moy,
               ROUND(MAX(sitescore)::numeric,1) as score_max
        FROM raw_data.iris WHERE type_iris='H';
    """, conn).iloc[0]
    return pd.read_sql("""
        SELECT
            COUNT(DISTINCT commune) as nb_communes,
            COUNT(*) as nb_iris,
            ROUND(AVG(sitescore)::numeric,1) as score_moy,
            ROUND(MAX(sitescore)::numeric,1) as score_max
        FROM raw_data.iris WHERE type_iris='H';
    """, get_conn()).iloc[0]

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='padding:24px 0 20px; border-bottom:1px solid #1E2D3D;
                    margin-bottom:20px;'>
            <div style='font-size:11px; color:#4A5568; letter-spacing:3px;
                        text-transform:uppercase; margin-bottom:8px;'>
                PLATFORM
            </div>
            <div style='font-size:22px; font-weight:900; color:#00D4FF;
                        letter-spacing:1px;'>
                SITE<span style='color:#E0E6ED;'>SCORE</span>
            </div>
            <div style='font-size:10px; color:#4A5568; margin-top:4px;
                        letter-spacing:1px;'>
                RETAIL LOCATION INTELLIGENCE · IDF
            </div>
        </div>
    """, unsafe_allow_html=True)

    communes_df = get_communes()
    communes_list = communes_df["commune"].tolist()

    st.markdown("<div style='font-size:10px;color:#4A5568;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>TARGET LOCATION</div>", unsafe_allow_html=True)
    commune_sel = st.selectbox("Commune", communes_list,
        index=communes_list.index("Montreuil") if "Montreuil" in communes_list else 0,
        label_visibility="collapsed")

    st.markdown("<div style='font-size:10px;color:#4A5568;letter-spacing:2px;text-transform:uppercase;margin:16px 0 6px;'>MIN SCORE THRESHOLD</div>", unsafe_allow_html=True)
    score_min = st.slider("Score", 0, 80, 20, label_visibility="collapsed")

    st.markdown("<div style='font-size:10px;color:#4A5568;letter-spacing:2px;text-transform:uppercase;margin:16px 0 6px;'>ANALYSIS MODE</div>", unsafe_allow_html=True)
    mode = st.selectbox("Mode", [
        "Global Score", "Anti-Concurrence", "High Revenue", "High Density"
    ], label_visibility="collapsed")

    st.markdown("<div style='font-size:10px;color:#4A5568;letter-spacing:2px;text-transform:uppercase;margin:16px 0 6px;'>RADIUS FILTER</div>", unsafe_allow_html=True)
    radius = st.selectbox("Radius", ["500m", "1km", "2km"],
                          index=1, label_visibility="collapsed")

    idf = get_idf_stats()
    st.markdown(f"""
        <div style='margin-top:24px; padding-top:20px; border-top:1px solid #1E2D3D;'>
            <div style='font-size:10px;color:#4A5568;letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:12px;'>
                IDF COVERAGE
            </div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>
                <div style='background:#111827;border-radius:8px;padding:12px;'>
                    <div style='font-size:20px;font-weight:800;color:#00D4FF;'>{idf['nb_communes']}</div>
                    <div style='font-size:9px;color:#4A5568;text-transform:uppercase;letter-spacing:1px;'>Communes</div>
                </div>
                <div style='background:#111827;border-radius:8px;padding:12px;'>
                    <div style='font-size:20px;font-weight:800;color:#00FF88;'>{idf['nb_iris']}</div>
                    <div style='font-size:9px;color:#4A5568;text-transform:uppercase;letter-spacing:1px;'>IRIS</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='margin-top:20px; padding-top:16px; border-top:1px solid #1E2D3D;
                    font-size:10px; color:#2D3748; text-align:center;'>
            MASSAMBA DIENG · 2026<br>
            PostGIS · Python · Streamlit
        </div>
    """, unsafe_allow_html=True)

# ── DONNÉES ───────────────────────────────────
df5   = get_top5(commune_sel)
df_all = get_all(commune_sel)

if df5.empty:
    st.markdown(f"""
        <div style='background:#0D1117;border:1px solid #1E2D3D;border-radius:12px;
                    padding:40px;text-align:center;margin-top:40px;'>
            <div style='font-size:32px;margin-bottom:12px;'>🔍</div>
            <div style='font-size:18px;color:#E0E6ED;font-weight:600;'>
                Aucun résultat pour "{commune_sel}"
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── HEADER ────────────────────────────────────
col_h1, col_h2, col_h3 = st.columns([3,1,1])
with col_h1:
    st.markdown(f"""
        <div style='padding:4px 0 20px;'>
            <div style='font-size:11px;color:#4A5568;letter-spacing:3px;
                        text-transform:uppercase;margin-bottom:6px;'>
                LOCATION INTELLIGENCE REPORT
            </div>
            <div style='font-size:30px;font-weight:900;color:#E0E6ED;line-height:1;'>
                {commune_sel.upper()}
                <span style='font-size:14px;color:#4A5568;font-weight:400;
                              margin-left:12px;'>
                    {df5.iloc[0]['dept'] if len(df5)>0 else ''} · Île-de-France
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ── KPI ROW ───────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)

kpis = [
    (k1, f"{df5.iloc[0]['sitescore']:.0f}", "BEST SITESCORE", "/100", "#00D4FF"),
    (k2, str(len(df_all)), "IRIS ANALYSÉS", f"sur {len(df_all)} total", "#00FF88"),
    (k3, str(int(df5.iloc[0]['nb_concurrents_1km'])), "CONCURRENTS ZONE 1", "dans 1km rayon", "#FFD700"),
    (k4, f"{df5.iloc[0]['revenu_median']:,}", "REVENU MÉDIAN", "€/an · Zone 1", "#FF6B35"),
    (k5, f"{df5.iloc[0]['densite_pop']:,}", "DENSITÉ POP", "hab/km² · Zone 1", "#C084FC"),
]

for col, val, label, delta, color in kpis:
    with col:
        st.markdown(f"""
            <div class="kpi-card" style="--accent:{color};">
                <p class="kpi-value">{val}</p>
                <p class="kpi-label">{label}</p>
                <p class="kpi-delta" style="color:{color}66;">{delta}</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── MAIN CONTENT ──────────────────────────────
left, right = st.columns([2,3])

with left:
    st.markdown('<div class="sec-header">TOP 5 — RECOMMENDED LOCATIONS</div>',
                unsafe_allow_html=True)

    for i, (_, row) in enumerate(df5.iterrows()):
        rank  = i + 1
        color = RANK_COLORS[i]
        label = RANK_LABELS[i]

        concurrents = int(row['nb_concurrents_1km'])
        if concurrents <= 2:   conc_color = "#00FF88"; conc_label = "FAIBLE"
        elif concurrents <= 5: conc_color = "#FFD700"; conc_label = "MODÉRÉ"
        else:                  conc_color = "#FF6B35"; conc_label = "ÉLEVÉ"

        st.markdown(f"""
            <div class="rank-card" style="--rank-color:{color};">
                <div style="display:flex;justify-content:space-between;align-items:start;">
                    <div style="flex:1;">
                        <div class="rank-num" style="color:{color};">
                            #{rank} · {label}
                        </div>
                        <div class="rank-name">{row['nom_iris']}</div>
                        <div class="rank-commune">
                            📍 {row['commune']} · Dept {row['dept']}
                        </div>
                        <div style="margin-top:10px;">
                            <span class="tag" style="background:{conc_color}22;
                                color:{conc_color};border:1px solid {conc_color}44;">
                                🏪 {concurrents} concurrents · {conc_label}
                            </span>
                            <span class="tag" style="background:#00D4FF22;
                                color:#00D4FF;border:1px solid #00D4FF44;">
                                💰 {int(row['revenu_median']):,}€
                            </span>
                            <span class="tag" style="background:#C084FC22;
                                color:#C084FC;border:1px solid #C084FC44;">
                                👥 {int(row['densite_pop']):,}/km²
                            </span>
                        </div>
                    </div>
                    <div style="text-align:right;margin-left:16px;">
                        <div class="rank-score" style="color:{color};">
                            {row['sitescore']:.0f}
                        </div>
                        <div style="font-size:10px;color:#4A5568;">/100</div>
                    </div>
                </div>
                <div class="score-bar-bg" style="--rank-color:{color};">
                    <div class="score-bar-fill"
                         style="width:{row['sitescore']}%;background:{color};"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="sec-header">SPATIAL ANALYSIS MAP</div>',
                unsafe_allow_html=True)

    center_lat = df_all["centroid_lat"].mean()
    center_lon = df_all["centroid_lon"].mean()

    carte = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="CartoDB positron"
    )

    # Tous les IRIS
    for _, row in df_all.iterrows():
        score = row["sitescore"]
        if score >= 50:   color = "#00D4FF"
        elif score >= 40: color = "#00FF88"
        elif score >= 30: color = "#FFD700"
        else:             color = "#2D3748"

        folium.CircleMarker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            weight=1,
            tooltip=f"{row['nom_iris']} · {row['sitescore']:.0f}/100",
            popup=folium.Popup(
                f"""<div style='font-family:monospace;font-size:12px;'>
                    <b>{row['nom_iris']}</b><br>
                    Score : <b>{row['sitescore']:.0f}/100</b><br>
                    Concurrents 1km : {row['nb_concurrents_1km']}<br>
                    Revenu : {row['revenu_median']:,}€<br>
                    Densité : {row['densite_pop']:,}/km²
                </div>""",
                max_width=220
            )
        ).add_to(carte)

    # TOP 5 markers
    for i, (_, row) in enumerate(df5.iterrows()):
        color = RANK_COLORS[i]
        folium.Marker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            icon=folium.DivIcon(
                html=f"""<div style='background:{color};color:#000;
                         font-weight:900;font-size:11px;
                         width:28px;height:28px;border-radius:50%;
                         display:flex;align-items:center;justify-content:center;
                         border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.5);'>
                         #{i+1}</div>""",
                icon_size=(28, 28),
                icon_anchor=(14, 14)
            ),
            tooltip=f"#{i+1} — {row['nom_iris']} · {row['sitescore']:.0f}/100"
        ).add_to(carte)

    st_folium(carte, width="stretch", height=520)

# ── CHARTS ROW ────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="sec-header">SCORE BREAKDOWN — ZONE 1</div>',
                unsafe_allow_html=True)
    top1 = df5.iloc[0]
    cats = ["Revenu", "Densité", "Concurrence", "Accessibilité", "Potentiel"]
    vals = [top1["score_revenu"], top1["score_densite"],
            top1["score_concurrence"], top1["score_accessibilite"],
            top1["score_potentiel"]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(0,212,255,0.15)",
        line=dict(color="#00D4FF", width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#0D1117",
            radialaxis=dict(
                visible=True, range=[0,100],
                gridcolor="#1E2D3D",
                tickfont=dict(color="#4A5568", size=9)
            ),
            angularaxis=dict(
                gridcolor="#1E2D3D",
                tickfont=dict(color="#8B9BB4", size=10)
            )
        ),
        paper_bgcolor="#0A0E1A",
        plot_bgcolor="#0A0E1A",
        showlegend=False,
        margin=dict(l=20,r=20,t=20,b=20),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown('<div class="sec-header">TOP 5 COMPARISON</div>',
                unsafe_allow_html=True)
    fig2 = go.Figure()
    for i, (_, row) in enumerate(df5.iterrows()):
        fig2.add_trace(go.Bar(
            x=[row["sitescore"]],
            y=[f"#{i+1} {row['nom_iris'][:20]}"],
            orientation="h",
            marker_color=RANK_COLORS[i],
            text=f"{row['sitescore']:.0f}",
            textposition="outside",
            textfont=dict(color=RANK_COLORS[i], size=11),
        ))
    fig2.update_layout(
        paper_bgcolor="#0A0E1A",
        plot_bgcolor="#0A0E1A",
        showlegend=False,
        margin=dict(l=0,r=40,t=10,b=10),
        height=280,
        xaxis=dict(range=[0,100], gridcolor="#1E2D3D",
                   tickfont=dict(color="#4A5568")),
        yaxis=dict(gridcolor="#1E2D3D",
                   tickfont=dict(color="#8B9BB4", size=10)),
        barmode="group",
    )
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.markdown('<div class="sec-header">SCORE DISTRIBUTION</div>',
                unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=df_all["sitescore"],
        nbinsx=15,
        marker_color="#00D4FF",
        opacity=0.7,
        marker_line=dict(color="#0A0E1A", width=1)
    ))
    fig3.update_layout(
        paper_bgcolor="#0A0E1A",
        plot_bgcolor="#0A0E1A",
        margin=dict(l=20,r=20,t=10,b=20),
        height=280,
        xaxis=dict(title="SiteScore", gridcolor="#1E2D3D",
                   tickfont=dict(color="#4A5568")),
        yaxis=dict(title="Nb IRIS", gridcolor="#1E2D3D",
                   tickfont=dict(color="#4A5568")),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── DATA TABLE ────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="sec-header">FULL IRIS DATASET — ' +
            commune_sel.upper() + '</div>', unsafe_allow_html=True)

df_show = df_all.rename(columns={
    "nom_iris":           "IRIS",
    "sitescore":          "SiteScore",
    "score_concurrence":  "Concurrence",
    "score_revenu":       "Revenu",
    "score_densite":      "Densité",
    "nb_concurrents_1km": "Conc. 1km",
    "revenu_median":      "Rev. Médian",
    "densite_pop":        "Densité Pop",
})[["IRIS","SiteScore","Concurrence","Revenu",
    "Densité","Conc. 1km","Rev. Médian","Densité Pop"]]

st.dataframe(
    df_show,
    use_container_width=True,
    height=250,
    hide_index=True,
)

st.markdown(f"""
    <div style='text-align:center; padding:20px 0 8px;
                font-size:10px; color:#2D3748; letter-spacing:2px;'>
        SITESCORE INTELLIGENCE PLATFORM · MASSAMBA DIENG · 2026 ·
        PostGIS · Python · Streamlit · OSM · INSEE
    </div>
""", unsafe_allow_html=True)