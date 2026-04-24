import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import os
import sys
import streamlit.components.v1 as components

st.set_page_config(
    page_title="SiteScore — Moteur d'implantation IDF",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #F0F4F8; }
    .main  { background-color: #F0F4F8; }
    .block-container { padding-top: 1.5rem; }
    [data-testid="stSidebar"] { background: #1A3557; border-right: none; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important; border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    .kpi {
        background: white; border-radius: 12px; padding: 20px 16px;
        border-top: 4px solid var(--c);
        box-shadow: 0 2px 8px rgba(26,53,87,0.08);
    }
    .kpi-val { font-size: 32px; font-weight: 800; color: var(--c); line-height: 1; margin: 0; }
    .kpi-lbl { font-size: 10px; color: #6B7280; text-transform: uppercase; letter-spacing: 1.5px; margin: 6px 0 0; }
    .kpi-sub { font-size: 11px; color: #9CA3AF; margin: 2px 0 0; }
    .rcard {
        background: white; border-radius: 12px; padding: 16px 20px;
        margin-bottom: 10px; border-left: 4px solid var(--rc);
        box-shadow: 0 2px 8px rgba(26,53,87,0.06);
    }
    .rcard-rank { font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--rc); }
    .rcard-name { font-size: 16px; font-weight: 700; color: #1A3557; margin: 4px 0 2px; }
    .rcard-commune { font-size: 12px; color: #6B7280; }
    .rcard-score { font-size: 42px; font-weight: 900; color: var(--rc); line-height: 1; }
    .pill { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin: 2px; }
    .bar-bg { background: #E5E7EB; border-radius: 4px; height: 5px; margin-top: 12px; }
    .sec {
        font-size: 10px; font-weight: 700; color: #6B7280;
        text-transform: uppercase; letter-spacing: 2.5px;
        margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #E5E7EB;
    }
    .banner {
        background: linear-gradient(135deg, #1A3557 0%, #2E6DA4 100%);
        border-radius: 16px; padding: 24px 32px; margin-bottom: 24px; color: white;
    }
    #MainMenu, footer, header { visibility: hidden; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

RANK_COLORS = ["#1A3557", "#2E6DA4", "#3B82F6", "#60A5FA", "#93C5FD"]
RANK_LABELS = ["OPTIMAL", "EXCELLENT", "BON", "CORRECT", "ACCEPTABLE"]
DATA_PATH   = "data/exports/sitescore_idf.csv"

@st.cache_data
def load_csv():
    return pd.read_csv(DATA_PATH)

@st.cache_data
def get_communes():
    df = load_csv()
    return df[["commune","dept"]].drop_duplicates().sort_values("commune")

@st.cache_data
def get_top5(commune):
    df = load_csv()
    r  = df[df["commune"].str.contains(commune, case=False, na=False)]
    return r.nlargest(5, "score_final")

@st.cache_data
def get_all(commune):
    df = load_csv()
    return df[df["commune"].str.contains(commune, case=False, na=False)].sort_values("score_final", ascending=False)

@st.cache_data
def get_idf_stats():
    df = load_csv()
    return pd.Series({"nb_communes": df["commune"].nunique(), "nb_iris": len(df)})

@st.cache_data
def get_multi(communes_list):
    df = load_csv()
    results = []
    for c in communes_list:
        top1 = df[df["commune"].str.contains(c, case=False, na=False)].nlargest(1, "score_final")
        if not top1.empty:
            results.append(top1.iloc[0])
    return pd.DataFrame(results) if results else pd.DataFrame()

if "page" not in st.session_state:
    st.session_state.page = "splash"

# ════════════════════════════════════════════════
# SPLASH
# ════════════════════════════════════════════════
if st.session_state.page == "splash":
    st.markdown("""
        <div style='min-height:95vh;background:linear-gradient(135deg,#0D2137,#1A3557,#2E6DA4);
                    display:flex;flex-direction:column;align-items:center;
                    justify-content:center;text-align:center;padding:40px;
                    border-radius:16px;margin-top:-1rem;'>
            <div style='font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:4px;
                        text-transform:uppercase;margin-bottom:16px;'>
                RETAIL LOCATION INTELLIGENCE · ÎLE-DE-FRANCE
            </div>
            <div style='font-size:68px;font-weight:900;line-height:1;color:white;'>
                SITE<span style='color:#60A5FA;'>SCORE</span>
            </div>
            <div style='width:50px;height:3px;background:linear-gradient(90deg,#60A5FA,#93C5FD);
                        margin:18px auto;border-radius:2px;'></div>
            <div style='font-size:13px;color:rgba(255,255,255,0.5);letter-spacing:3px;
                        text-transform:uppercase;margin-bottom:40px;'>
                MOTEUR D'IMPLANTATION COMMERCIALE · ML + EXPERT RULES
            </div>
            <div style='display:flex;gap:40px;margin-bottom:48px;flex-wrap:wrap;justify-content:center;'>
                <div><div style='font-size:36px;font-weight:900;color:white;'>351</div>
                     <div style='font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Communes</div></div>
                <div style='width:1px;background:rgba(255,255,255,0.1);'></div>
                <div><div style='font-size:36px;font-weight:900;color:#60A5FA;'>5 264</div>
                     <div style='font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>IRIS analysés</div></div>
                <div style='width:1px;background:rgba(255,255,255,0.1);'></div>
                <div><div style='font-size:36px;font-weight:900;color:#93C5FD;'>7 259</div>
                     <div style='font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Supermarchés</div></div>
                <div style='width:1px;background:rgba(255,255,255,0.1);'></div>
                <div><div style='font-size:36px;font-weight:900;color:#BFDBFE;'>68%</div>
                     <div style='font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>RF Accuracy</div></div>
            </div>
            <div style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
                        border-radius:14px;padding:24px 40px;margin-bottom:40px;'>
                <div style='font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:3px;
                            text-transform:uppercase;margin-bottom:10px;'>RÉALISÉ PAR</div>
                <div style='font-size:26px;font-weight:900;color:white;letter-spacing:2px;'>
                    Massamba <span style='color:#60A5FA;'>DIENG</span>
                </div>
                <div style='font-size:11px;color:rgba(255,255,255,0.4);margin-top:4px;
                            letter-spacing:1px;text-transform:uppercase;'>
                    Chargé d'études Géomarketing · Master UPEC
                </div>
                <div style='display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap;'>
                    <span style='font-size:10px;color:#60A5FA;background:rgba(96,165,250,0.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(96,165,250,0.3);'>Python</span>
                    <span style='font-size:10px;color:#34D399;background:rgba(52,211,153,0.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(52,211,153,0.3);'>PostGIS</span>
                    <span style='font-size:10px;color:#FCD34D;background:rgba(252,211,77,0.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(252,211,77,0.3);'>Random Forest</span>
                    <span style='font-size:10px;color:#C084FC;background:rgba(192,132,252,0.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(192,132,252,0.3);'>DVF</span>
                    <span style='font-size:10px;color:#FB923C;background:rgba(251,146,60,0.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(251,146,60,0.3);'>OSM</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("🚀  Explorer le dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    st.stop()

# ════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════
communes_df   = get_communes()
communes_list = communes_df["commune"].tolist()
idf           = get_idf_stats()

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='padding:20px 0 20px;border-bottom:1px solid rgba(255,255,255,0.15);
                    margin-bottom:20px;text-align:center;'>
            <div style='font-size:22px;font-weight:900;color:white;letter-spacing:1px;'>
                SITE<span style='color:#60A5FA;'>SCORE</span>
            </div>
            <div style='font-size:9px;color:rgba(255,255,255,0.4);margin-top:4px;
                        letter-spacing:2px;text-transform:uppercase;'>
                Retail Location Intelligence
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:10px;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;'>MODE D'ANALYSE</p>", unsafe_allow_html=True)
    mode = st.selectbox(
        "Mode",
        ["🔍 Analyse d'une commune", "📊 Comparer plusieurs communes", "🗺️ Déserts commerciaux IDF"],
        label_visibility="collapsed"
    )

    st.markdown("<p style='font-size:10px;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:2px;margin:16px 0 6px;'>COMMUNE CIBLE</p>", unsafe_allow_html=True)

    if mode == "🔍 Analyse d'une commune":
        commune_sel   = st.selectbox("Commune", communes_list,
            index=communes_list.index("Montreuil") if "Montreuil" in communes_list else 0,
            label_visibility="collapsed")
        communes_comp = []
        st.markdown("""
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:12px;margin-top:12px;'>
                <div style='font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;'>À PROPOS DE CE MODE</div>
                <div style='font-size:11px;color:rgba(255,255,255,0.6);line-height:1.6;'>
                    Analyse détaillée d'une commune :<br>• TOP 5 emplacements<br>• Carte interactive<br>• Scores détaillés<br>• Export PDF
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif mode == "📊 Comparer plusieurs communes":
        commune_sel   = communes_list[0]
        communes_comp = st.multiselect("Communes", communes_list,
            default=[c for c in ["Montreuil","Vincennes","Pantin","Bobigny"] if c in communes_list][:3],
            label_visibility="collapsed")
        st.markdown("""
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:12px;margin-top:12px;'>
                <div style='font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;'>À PROPOS DE CE MODE</div>
                <div style='font-size:11px;color:rgba(255,255,255,0.6);line-height:1.6;'>
                    Compare plusieurs communes :<br>• Radar multi-critères<br>• Classement comparatif<br>• Meilleur IRIS par ville
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        commune_sel   = communes_list[0]
        communes_comp = []
        st.markdown("""
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:12px;margin-top:12px;'>
                <div style='font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;'>À PROPOS DE CE MODE</div>
                <div style='font-size:11px;color:rgba(255,255,255,0.6);line-height:1.6;'>
                    Carte IDF complète :<br>• Déserts commerciaux<br>• Opportunités fortes<br>• CA potentiel estimé
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.15);'>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>
                <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:10px;text-align:center;'>
                    <div style='font-size:18px;font-weight:800;color:white;'>{idf['nb_communes']}</div>
                    <div style='font-size:8px;color:rgba(255,255,255,0.4);text-transform:uppercase;'>Communes</div>
                </div>
                <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:10px;text-align:center;'>
                    <div style='font-size:18px;font-weight:800;color:#60A5FA;'>{idf['nb_iris']}</div>
                    <div style='font-size:8px;color:rgba(255,255,255,0.4);text-transform:uppercase;'>IRIS</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Accueil", use_container_width=True):
        st.session_state.page = "splash"
        st.rerun()

# ════════════════════════════════════════════════
# MODE COMPARAISON
# ════════════════════════════════════════════════
if mode == "📊 Comparer plusieurs communes" and communes_comp:
    st.markdown(f"""
        <div class="banner">
            <p style='font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:3px;text-transform:uppercase;margin:0 0 6px;'>COMPARAISON MULTI-COMMUNES</p>
            <p style='font-size:26px;font-weight:800;color:white;margin:0;'>{len(communes_comp)} communes analysées</p>
        </div>
    """, unsafe_allow_html=True)

    df_comp = get_multi(communes_comp)
    if df_comp.empty:
        st.warning("Aucun résultat.")
        st.stop()

    c1, c2 = st.columns([3,2])
    with c1:
        st.markdown('<div class="sec">RADAR MULTI-CRITÈRES</div>', unsafe_allow_html=True)
        cats    = ["Score Final","SiteScore","RF Score","Concurrence","Revenu","Foncier"]
        metrics = ["score_final","sitescore","rf_score","score_concurrence","score_revenu","score_foncier"]
        colors  = ["#1A3557","#2E6DA4","#3B82F6","#60A5FA","#93C5FD","#BFDBFE"]
        fig = go.Figure()
        for i, (_, row) in enumerate(df_comp.iterrows()):
            vals = [float(row.get(m, 0)) for m in metrics]
            c    = colors[i % len(colors)]
            r,g,b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
            fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=cats+[cats[0]],
                fill="toself", name=str(row["commune"]),
                line=dict(color=c, width=2),
                fillcolor=f"rgba({r},{g},{b},0.12)",
            ))
        fig.update_layout(
            polar=dict(bgcolor="white",
                radialaxis=dict(visible=True,range=[0,100],gridcolor="#E5E7EB",tickfont=dict(color="#9CA3AF",size=9)),
                angularaxis=dict(gridcolor="#E5E7EB",tickfont=dict(color="#374151",size=10))),
            paper_bgcolor="#F0F4F8", showlegend=True,
            legend=dict(font=dict(color="#374151",size=10)),
            margin=dict(l=40,r=40,t=40,b=40), height=420,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec">CLASSEMENT COMPARATIF</div>', unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_comp.sort_values("score_final", ascending=False).iterrows()):
            color = RANK_COLORS[min(i, len(RANK_COLORS)-1)]
            st.markdown(f"""
                <div class="rcard" style="--rc:{color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div class="rcard-rank">#{i+1}</div>
                            <div class="rcard-name">{row['commune']}</div>
                            <div class="rcard-commune">{row['nom_iris']} · Dept {row['dept']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="rcard-score">{row['score_final']:.0f}</div>
                            <div style="font-size:10px;color:#9CA3AF;">/100</div>
                        </div>
                    </div>
                    <div class="bar-bg"><div style="background:{color};height:5px;border-radius:4px;width:{row['score_final']}%;"></div></div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sec" style="margin-top:24px;">TABLEAU COMPARATIF DÉTAILLÉ</div>', unsafe_allow_html=True)
    cols_ok = [c for c in ["commune","nom_iris","score_final","sitescore","rf_score","nb_concurrents_1km","revenu_median","prix_m2_median"] if c in df_comp.columns]
    st.dataframe(df_comp[cols_ok].rename(columns={
        "commune":"Commune","nom_iris":"Meilleur IRIS","score_final":"Score Final",
        "sitescore":"SiteScore","rf_score":"RF Score","nb_concurrents_1km":"Conc. 1km",
        "revenu_median":"Revenu €","prix_m2_median":"Prix m²",
    }), use_container_width=True, hide_index=True)
    st.stop()

# ════════════════════════════════════════════════
# MODE DÉSERTS COMMERCIAUX
# ════════════════════════════════════════════════
if mode == "🗺️ Déserts commerciaux IDF":
    st.markdown("""
        <div class="banner">
            <p style='font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:3px;text-transform:uppercase;margin:0 0 6px;'>ANALYSE TERRITORIALE</p>
            <p style='font-size:26px;font-weight:800;color:white;margin:0;'>Déserts Commerciaux — Île-de-France</p>
        </div>
    """, unsafe_allow_html=True)

    df_all_idf = load_csv()
    desert_mask = (
        (df_all_idf["nb_concurrents_500m"] == 0) &
        (df_all_idf["nb_concurrents_1km"] <= 3) &
        (df_all_idf["ca_potentiel_an"] >= 500000) &
        (df_all_idf["densite_pop"] >= 500)
    )
    opp_mask = (
        (df_all_idf["nb_concurrents_1km"] <= 5) &
        (df_all_idf["ca_potentiel_an"] >= 800000) &
        (df_all_idf["densite_pop"] >= 1000)
    )

    nb_deserts = desert_mask.sum()
    nb_opps    = opp_mask.sum()
    ca_total   = df_all_idf[desert_mask]["ca_potentiel_an"].sum()
    ca_opp     = df_all_idf[opp_mask]["ca_potentiel_an"].sum()

    k1,k2,k3,k4 = st.columns(4)
    for col, val, lbl, sub, color in [
        (k1, str(nb_deserts),         "Déserts commerciaux", "0 conc. 500m",   "#DC2626"),
        (k2, str(nb_opps),            "Opportunités",        "≤5 conc. 1km",   "#D97706"),
        (k3, f"{ca_total/1e6:.1f}M€", "CA déserts total",   "potentiel/an",    "#1A3557"),
        (k4, f"{ca_opp/1e6:.1f}M€",  "CA opportunités",     "potentiel/an",    "#3B82F6"),
    ]:
        with col:
            st.markdown(f'<div class="kpi" style="--c:{color};"><p class="kpi-val">{val}</p><p class="kpi-lbl">{lbl}</p><p class="kpi-sub">{sub}</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Carte Plotly des déserts
    st.markdown('<div class="sec">🗺️ CARTE INTERACTIVE — DÉSERTS COMMERCIAUX IDF</div>',
                unsafe_allow_html=True)

    df_map = load_csv().copy()
    df_map["categorie"] = "standard"
    df_map.loc[
        (df_map["nb_concurrents_500m"]==0) &
        (df_map["nb_concurrents_1km"]<=3) &
        (df_map["ca_potentiel_an"]>=500000) &
        (df_map["densite_pop"]>=500), "categorie"] = "desert"
    df_map.loc[
        (df_map["nb_concurrents_1km"]<=5) &
        (df_map["ca_potentiel_an"]>=800000) &
        (df_map["densite_pop"]>=1000) &
        (df_map["categorie"]!="desert"), "categorie"] = "opportunite_forte"
    df_map.loc[
        (df_map["nb_concurrents_1km"]<=8) &
        (df_map["ca_potentiel_an"]>=400000) &
        (df_map["categorie"]=="standard"), "categorie"] = "opportunite_moyenne"

    cat_config = {
        "desert":             {"color":"#DC2626", "size":16, "label":"🔴 Désert commercial"},
        "opportunite_forte":  {"color":"#F59E0B", "size":12, "label":"🟡 Opportunité forte"},
        "opportunite_moyenne":{"color":"#3B82F6", "size":8,  "label":"🔵 Opportunité moyenne"},
    }

    fig_map = go.Figure()
    for cat, cfg in cat_config.items():
        sub = df_map[df_map["categorie"]==cat]
        if sub.empty:
            continue
        ca_vals = sub["ca_potentiel_an"].apply(
            lambda x: f"{x/1e6:.1f}M€" if x>=1e6 else f"{x/1e3:.0f}k€")
        fig_map.add_trace(go.Scattermapbox(
            lat=sub["centroid_lat"],
            lon=sub["centroid_lon"],
            mode="markers",
            marker=dict(size=cfg["size"], color=cfg["color"], opacity=0.85),
            name=cfg["label"],
            text=sub["nom_iris"] + " · " + sub["commune"],
            customdata=list(zip(
                sub["commune"], sub["nom_iris"],
                ca_vals, sub["nb_concurrents_1km"].astype(int),
                sub["revenu_median"].astype(int)
            )),
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>"
                "%{customdata[0]}<br>"
                "CA potentiel : <b>%{customdata[2]}</b><br>"
                "Concurrents 1km : %{customdata[3]}<br>"
                "Revenu médian : %{customdata[4]:,}€"
                "<extra></extra>"
            )
        ))

    fig_map.update_layout(
        mapbox=dict(style="carto-positron",
                    center=dict(lat=48.8566, lon=2.3522), zoom=8),
        paper_bgcolor="#F0F4F8",
        margin=dict(l=0,r=0,t=0,b=0),
        height=550,
        legend=dict(
            bgcolor="white", bordercolor="#E5E7EB", borderwidth=1,
            font=dict(size=11, color="#374151"),
            x=0.01, y=0.99
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ════════════════════════════════════════════════
# MODE ANALYSE COMMUNE
# ════════════════════════════════════════════════
df5    = get_top5(commune_sel)
df_all = get_all(commune_sel)

if df5.empty:
    st.warning(f"Aucun résultat pour '{commune_sel}'.")
    st.stop()

top1 = df5.iloc[0]

st.markdown(f"""
    <div class="banner">
        <p style='font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:3px;text-transform:uppercase;margin:0 0 6px;'>LOCATION INTELLIGENCE REPORT</p>
        <p style='font-size:28px;font-weight:900;color:white;margin:0;line-height:1;'>
            {commune_sel.upper()}
            <span style='font-size:14px;color:rgba(255,255,255,0.5);font-weight:400;margin-left:12px;'>
                Dept {top1['dept']} · Île-de-France · {len(df_all)} IRIS analysés
            </span>
        </p>
    </div>
""", unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
ca_val = top1.get('ca_potentiel_an', 0)
ca_str = f"{ca_val/1e6:.1f}M€" if ca_val >= 1e6 else f"{ca_val/1e3:.0f}k€"
for col, val, lbl, sub, color in [
    (k1, f"{top1['score_final']:.0f}", "Score Final",  "SiteScore + RF",   "#1A3557"),
    (k2, f"{top1['sitescore']:.0f}",   "SiteScore",    "Règles expertes",  "#2E6DA4"),
    (k3, f"{top1['rf_score']:.0f}",    "RF Score",     "Machine learning", "#3B82F6"),
    (k4, str(int(top1['nb_concurrents_1km'])), "Concurrents", "dans 1km", "#DC2626"),
    (k5, ca_str,                       "CA Potentiel", "estimé/an zone 1", "#7C3AED"),
]:
    with col:
        st.markdown(f'<div class="kpi" style="--c:{color};"><p class="kpi-val">{val}</p><p class="kpi-lbl">{lbl}</p><p class="kpi-sub">{sub}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([2,3])

with left:
    st.markdown('<div class="sec">🏆 TOP 5 EMPLACEMENTS RECOMMANDÉS</div>', unsafe_allow_html=True)
    for i, (_, row) in enumerate(df5.iterrows()):
        color = RANK_COLORS[i]
        label = RANK_LABELS[i]
        nb_conc = int(row['nb_concurrents_1km'])
        if nb_conc <= 2:   cc="#16A34A"; cl="FAIBLE"
        elif nb_conc <= 5: cc="#D97706"; cl="MODÉRÉ"
        else:              cc="#DC2626"; cl="ÉLEVÉ"
        ca = row.get('ca_potentiel_an', 0)
        ca_display = f"{ca/1e6:.1f}M€" if ca >= 1e6 else f"{ca/1e3:.0f}k€"

        st.markdown(f"""
            <div class="rcard" style="--rc:{color};">
                <div style="display:flex;justify-content:space-between;align-items:start;">
                    <div style="flex:1;">
                        <div class="rcard-rank">#{i+1} · {label}</div>
                        <div class="rcard-name">{row['nom_iris']}</div>
                        <div class="rcard-commune">📍 {row['commune']} · Dept {row['dept']}</div>
                        <div style="margin-top:10px;">
                            <span class="pill" style="background:{cc}18;color:{cc};border:1px solid {cc}33;">
                                🏪 {nb_conc} · {cl}
                            </span>
                            <span class="pill" style="background:#1A355718;color:#1A3557;border:1px solid #1A355733;">
                                💰 {int(row['revenu_median']):,}€
                            </span>
                            <span class="pill" style="background:#7C3AED18;color:#7C3AED;border:1px solid #7C3AED33;">
                                💵 CA: {ca_display}
                            </span>
                        </div>
                    </div>
                    <div style="text-align:right;margin-left:16px;">
                        <div class="rcard-score">{row['score_final']:.0f}</div>
                        <div style="font-size:10px;color:#9CA3AF;">/100</div>
                        <div style="font-size:10px;color:#9CA3AF;">RF:{row['rf_score']:.0f}</div>
                    </div>
                </div>
                <div class="bar-bg"><div style="background:{color};height:5px;border-radius:4px;width:{row['score_final']}%;"></div></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📄 Exporter le rapport PDF", use_container_width=True):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("export_pdf", "notebooks/09_export_pdf.py")
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            pdf_path = mod.generate_pdf(commune_sel)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Télécharger le PDF", data=f.read(),
                    file_name=f"SiteScore_{commune_sel}.pdf",
                    mime="application/pdf", use_container_width=True,
                )
        except Exception as e:
            st.error(f"Erreur PDF : {e}")

with right:
    st.markdown('<div class="sec">🗺️ CARTE DES RECOMMANDATIONS</div>', unsafe_allow_html=True)
    center_lat = df_all["centroid_lat"].mean()
    center_lon = df_all["centroid_lon"].mean()
    carte = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="CartoDB positron")

    for _, row in df_all.iterrows():
        score = row["score_final"]
        if score >= 65:   c="#1A3557"
        elif score >= 55: c="#2E6DA4"
        elif score >= 45: c="#60A5FA"
        else:             c="#CBD5E1"
        folium.CircleMarker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            radius=7, color=c, fill=True, fill_color=c, fill_opacity=0.8, weight=1,
            tooltip=f"{row['nom_iris']} · {row['score_final']:.0f}/100",
            popup=folium.Popup(
                f"<b>{row['nom_iris']}</b><br>Score : <b>{row['score_final']:.0f}/100</b><br>"
                f"RF : {row['rf_score']:.0f} | Conc. 1km : {row['nb_concurrents_1km']}<br>"
                f"Revenu : {int(row['revenu_median']):,}€", max_width=220)
        ).add_to(carte)

    for i, (_, row) in enumerate(df5.iterrows()):
        folium.Marker(
            location=[row["centroid_lat"], row["centroid_lon"]],
            icon=folium.DivIcon(
                html=f"<div style='background:{RANK_COLORS[i]};color:white;font-weight:900;font-size:11px;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);'>#{i+1}</div>",
                icon_size=(28,28), icon_anchor=(14,14)
            ),
            tooltip=f"#{i+1} — {row['nom_iris']} · {row['score_final']:.0f}/100"
        ).add_to(carte)

    st_folium(carte, width=None, height=520)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="sec">PROFIL — ZONE #1</div>', unsafe_allow_html=True)
    cats = ["Revenu","Densité","Concurrence","Accessibilité","Potentiel","Foncier"]
    vals = [float(top1.get(f,0)) for f in ["score_revenu","score_densite","score_concurrence","score_accessibilite","score_potentiel","score_foncier"]]
    fig1 = go.Figure()
    fig1.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]], fill="toself",
        fillcolor="rgba(26,53,87,0.12)", line=dict(color="#1A3557", width=2)))
    fig1.update_layout(
        polar=dict(bgcolor="white",
            radialaxis=dict(visible=True,range=[0,100],gridcolor="#E5E7EB",tickfont=dict(color="#9CA3AF",size=9)),
            angularaxis=dict(gridcolor="#E5E7EB",tickfont=dict(color="#374151",size=10))),
        paper_bgcolor="#F0F4F8", showlegend=False, margin=dict(l=20,r=20,t=20,b=20), height=300)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown('<div class="sec">COMPARAISON TOP 5</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for i, (_, row) in enumerate(df5.iterrows()):
        fig2.add_trace(go.Bar(
            x=[row["score_final"]], y=[f"#{i+1} {row['nom_iris'][:18]}"],
            orientation="h", marker_color=RANK_COLORS[i],
            text=f"{row['score_final']:.0f}", textposition="outside",
            textfont=dict(color=RANK_COLORS[i],size=11)))
    fig2.update_layout(
        paper_bgcolor="#F0F4F8", plot_bgcolor="white", showlegend=False,
        margin=dict(l=0,r=40,t=10,b=10), height=300,
        xaxis=dict(range=[0,100],gridcolor="#E5E7EB",tickfont=dict(color="#9CA3AF")),
        yaxis=dict(gridcolor="#E5E7EB",tickfont=dict(color="#374151",size=10)))
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.markdown('<div class="sec">DISTRIBUTION DES SCORES</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(x=df_all["score_final"], nbinsx=15,
        marker_color="#1A3557", opacity=0.8, marker_line=dict(color="white",width=1)))
    fig3.update_layout(
        paper_bgcolor="#F0F4F8", plot_bgcolor="white",
        margin=dict(l=20,r=20,t=10,b=20), height=300,
        xaxis=dict(title="Score Final",gridcolor="#E5E7EB",tickfont=dict(color="#9CA3AF")),
        yaxis=dict(title="Nb IRIS",gridcolor="#E5E7EB",tickfont=dict(color="#9CA3AF")))
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f'<div class="sec">TOUS LES IRIS — {commune_sel.upper()}</div>', unsafe_allow_html=True)
cols_show = ["nom_iris","score_final","sitescore","rf_score","score_concurrence","score_revenu","score_foncier","nb_concurrents_1km","revenu_median","prix_m2_median"]
cols_ok = [c for c in cols_show if c in df_all.columns]
st.dataframe(df_all[cols_ok].rename(columns={
    "nom_iris":"IRIS","score_final":"Score Final","sitescore":"SiteScore","rf_score":"RF Score",
    "score_concurrence":"Concurrence","score_revenu":"Revenu","score_foncier":"Foncier",
    "nb_concurrents_1km":"Conc. 1km","revenu_median":"Rev. €","prix_m2_median":"Prix m²",
}), use_container_width=True, height=280, hide_index=True)

st.markdown("""
    <div style='text-align:center;padding:20px 0 8px;font-size:10px;color:#9CA3AF;letter-spacing:1px;'>
        SiteScore · Massamba DIENG · 2026 · PostGIS · Python · Random Forest · DVF 2024 · OSM · INSEE
    </div>
""", unsafe_allow_html=True)