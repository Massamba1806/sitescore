import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, KeepTogether)
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

def generate_pdf(commune: str, output_path: str = None):

    df = pd.read_csv("data/exports/sitescore_idf.csv")
    df_commune = df[
        df["commune"].str.contains(commune, case=False, na=False)
    ].sort_values("score_final", ascending=False)

    if df_commune.empty:
        print(f"❌ Aucun résultat pour '{commune}'")
        return

    top5 = df_commune.head(5)
    top1 = top5.iloc[0]

    if output_path is None:
        os.makedirs("data/exports/pdf", exist_ok=True)
        output_path = f"data/exports/pdf/SiteScore_{commune.replace(' ','_')}.pdf"

    # Couleurs
    NAVY    = HexColor("#1A3557")
    BLUE    = HexColor("#2E6DA4")
    ACCENT  = HexColor("#3B82F6")
    LIGHT   = HexColor("#EBF4FF")
    DARK    = HexColor("#1F2937")
    GRAY    = HexColor("#6B7280")
    LGRAY   = HexColor("#F3F4F6")
    GREEN   = HexColor("#059669")
    ORANGE  = HexColor("#D97706")
    RED     = HexColor("#DC2626")
    WHITE_C = white
    RANK_C  = [HexColor("#1A3557"), HexColor("#2E6DA4"),
               HexColor("#3B82F6"), HexColor("#60A5FA"), HexColor("#93C5FD")]

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
    )

    def ps(name, **kw):
        base = getSampleStyleSheet()["Normal"]
        return ParagraphStyle(name, parent=base, **kw)

    S_title   = ps("t", fontSize=26, fontName="Helvetica-Bold",   textColor=white,  leading=30)
    S_sub     = ps("s", fontSize=11, fontName="Helvetica",         textColor=HexColor("#93C5FD"), leading=14)
    S_kpi_v   = ps("kv",fontSize=28, fontName="Helvetica-Bold",   alignment=TA_CENTER, leading=32)
    S_kpi_l   = ps("kl",fontSize=8,  fontName="Helvetica-Bold",   textColor=GRAY,   alignment=TA_CENTER, leading=10, spaceBefore=4, textTransform="uppercase")
    S_sec     = ps("sc",fontSize=9,  fontName="Helvetica-Bold",   textColor=NAVY,   leading=11, spaceBefore=16, spaceAfter=6, textTransform="uppercase")
    S_body    = ps("bd",fontSize=9,  fontName="Helvetica",         textColor=DARK,   leading=13)
    S_bullet  = ps("bu",fontSize=9,  fontName="Helvetica",         textColor=DARK,   leading=13, leftIndent=12, bulletIndent=2)
    S_rank_n  = ps("rn",fontSize=7,  fontName="Helvetica-Bold",   leading=9,  spaceAfter=2)
    S_rank_t  = ps("rt",fontSize=12, fontName="Helvetica-Bold",   textColor=DARK,   leading=14)
    S_rank_c  = ps("rc",fontSize=8,  fontName="Helvetica",         textColor=GRAY,   leading=10, spaceAfter=4)
    S_rank_d  = ps("rd",fontSize=8,  fontName="Helvetica",         textColor=DARK,   leading=11)
    S_reco_t  = ps("ret",fontSize=10,fontName="Helvetica-Bold",   textColor=NAVY,   leading=12, spaceBefore=8)
    S_reco_b  = ps("reb",fontSize=9, fontName="Helvetica",         textColor=DARK,   leading=13)
    S_footer  = ps("ft",fontSize=7,  fontName="Helvetica",         textColor=GRAY,   alignment=TA_CENTER, leading=9)
    S_insight = ps("in",fontSize=9,  fontName="Helvetica",         textColor=DARK,   leading=13, leftIndent=8)

    W = A4[0] - 3.6*cm
    story = []

    # ── HEADER ───────────────────────────────
    hdr = Table([[
        Paragraph(f'<font size="9" color="#93C5FD">LOCATION INTELLIGENCE REPORT</font><br/>'
                  f'<font size="26"><b>{commune.upper()}</b></font><br/>'
                  f'<font size="10" color="#BFDBFE">Île-de-France · Analyse d\'implantation commerciale</font>',
                  S_title),
        Paragraph('<font size="22"><b><font color="#60A5FA">SITE</font>'
                  '<font color="white">SCORE</font></b></font><br/>'
                  '<font size="7" color="#4A5568">RETAIL LOCATION INTELLIGENCE</font>',
                  ps("logo", fontSize=22, fontName="Helvetica-Bold",
                     alignment=TA_RIGHT, textColor=white))
    ]], colWidths=[12*cm, 5.4*cm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,-1), NAVY),
        ("PADDING",     (0,0),(-1,-1), 14),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 0.35*cm))

    # ── KPIs ─────────────────────────────────
    def kpi_cell(val, label, color):
        return [
            Paragraph(f'<font color="#{color.hexval()[2:]}">{val}</font>', S_kpi_v),
            Paragraph(label, S_kpi_l)
        ]

    kpi_data = [[
        Paragraph(f'<font color="#1A3557"><b>{top1["score_final"]:.0f}</b></font>', S_kpi_v),
        Paragraph(f'<font color="#2E6DA4"><b>{top1["sitescore"]:.0f}</b></font>', S_kpi_v),
        Paragraph(f'<font color="#3B82F6"><b>{top1["rf_score"]:.0f}</b></font>', S_kpi_v),
        Paragraph(f'<font color="#DC2626"><b>{int(top1["nb_concurrents_1km"])}</b></font>', S_kpi_v),
        Paragraph(f'<font color="#7C3AED"><b>{int(top1["prix_m2_median"]):,}€</b></font>', S_kpi_v),
    ],[
        Paragraph("SCORE FINAL", S_kpi_l),
        Paragraph("SITESCORE", S_kpi_l),
        Paragraph("RF SCORE", S_kpi_l),
        Paragraph("CONCURRENTS 1KM", S_kpi_l),
        Paragraph("PRIX M² DVF", S_kpi_l),
    ]]
    kpi_t = Table(kpi_data, colWidths=[W/5]*5)
    kpi_t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,-1), LGRAY),
        ("PADDING",     (0,0),(-1,-1), 10),
        ("ALIGN",       (0,0),(-1,-1), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("LINEAFTER",   (0,0),(3,1),   0.5, HexColor("#E5E7EB")),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 4),
    ]))
    story.append(kpi_t)
    story.append(Spacer(1, 0.35*cm))

    # ── TOP 5 ─────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB"), spaceAfter=6))
    story.append(Paragraph("TOP 5 — EMPLACEMENTS RECOMMANDÉS", S_sec))

    MEDALS = ["#1 OPTIMAL", "#2 EXCELLENT", "#3 BON", "#4 CORRECT", "#5 ACCEPTABLE"]

    for i, (_, row) in enumerate(top5.iterrows()):
        rc = RANK_C[i]
        medal = MEDALS[i]
        nb_c = int(row['nb_concurrents_1km'])
        conc_label = "FAIBLE" if nb_c<=2 else ("MODÉRÉ" if nb_c<=5 else "ÉLEVÉ")

        left = [
            Paragraph(f'<font color="#{rc.hexval()[2:]}" size="8"><b>{medal}</b></font>', S_rank_n),
            Paragraph(str(row["nom_iris"]), S_rank_t),
            Paragraph(f'{row["commune"]} · Dept {row["dept"]}', S_rank_c),
            Paragraph(
                f'Concurrents 1km : <b>{nb_c}</b> ({conc_label})   |   '
                f'Revenu médian : <b>{int(row["revenu_median"]):,}€</b>   |   '
                f'Prix m² : <b>{int(row["prix_m2_median"]):,}€</b>',
                S_rank_d
            ),
        ]
        right = [
            Paragraph(f'<font color="#{rc.hexval()[2:]}" size="28"><b>{row["score_final"]:.0f}</b></font>',
                      ps("sc2", fontSize=28, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=32)),
            Paragraph("/100", ps("s100", fontSize=8, fontName="Helvetica", textColor=GRAY, alignment=TA_CENTER)),
            Paragraph(f'RF: {row["rf_score"]:.0f}', ps("srf", fontSize=7, fontName="Helvetica", textColor=GRAY, alignment=TA_CENTER)),
        ]

        row_t = Table([[left, right]], colWidths=[13.5*cm, 3.9*cm])
        row_t.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), LGRAY),
            ("LINEAFTER",   (0,0),(0,0),   0.5, HexColor("#E5E7EB")),
            ("LINEBEFORE",  (0,0),(0,0),   3,   rc),
            ("PADDING",     (0,0),(-1,-1), 8),
            ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
            ("TOPPADDING",  (0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ]))
        story.append(row_t)
        story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 0.3*cm))

    # ── ANALYSE & RECOMMANDATIONS ─────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB"), spaceAfter=6))
    story.append(Paragraph("ANALYSE & RECOMMANDATIONS", S_sec))

    score_moy = df_commune["score_final"].mean()
    score_max = df_commune["score_final"].max()
    nb_iris   = len(df_commune)
    nb_faible = len(df_commune[df_commune["nb_concurrents_1km"] <= 2])
    rev_moy   = df_commune["revenu_median"].mean()
    prix_moy  = df_commune["prix_m2_median"].mean()

    # Analyse automatique
    if score_max >= 70:
        niveau = "très attractif"
        conseil = "fort potentiel d'implantation"
    elif score_max >= 55:
        niveau = "modérément attractif"
        conseil = "potentiel intéressant mais marché concurrentiel"
    else:
        niveau = "difficile"
        conseil = "concurrence élevée — étudier des communes voisines"

    if nb_faible > 0:
        conc_insight = f"{nb_faible} IRIS présentent une concurrence faible (≤2 concurrents dans 1km) — opportunités directes d'implantation."
    else:
        conc_insight = "Tous les IRIS présentent une concurrence élevée — différenciation par format ou positionnement recommandée."

    if rev_moy >= 30000:
        rev_insight = f"Revenu médian moyen de {rev_moy:,.0f}€ — profil CSP+ favorable à une enseigne positionnée milieu/haut de gamme."
    elif rev_moy >= 22000:
        rev_insight = f"Revenu médian moyen de {rev_moy:,.0f}€ — profil mixte, adapté à une enseigne discount ou généraliste."
    else:
        rev_insight = f"Revenu médian moyen de {rev_moy:,.0f}€ — profil populaire, fort potentiel pour une enseigne hard-discount."

    reco_data = [
        [
            Paragraph("📊 Synthèse du marché", S_reco_t),
            Paragraph(
                f"La commune de {commune} présente un marché {niveau} pour la grande distribution "
                f"({conseil}). Sur {nb_iris} IRIS analysés, le meilleur score atteint "
                f"{score_max:.0f}/100 avec un score moyen de {score_moy:.1f}/100.",
                S_reco_b
            ),
        ],
        [
            Paragraph("🏪 Analyse concurrentielle", S_reco_t),
            Paragraph(conc_insight, S_reco_b),
        ],
        [
            Paragraph("💰 Profil socio-économique", S_reco_t),
            Paragraph(rev_insight, S_reco_b),
        ],
        [
            Paragraph("🏠 Contexte foncier", S_reco_t),
            Paragraph(
                f"Prix immobilier médian de {prix_moy:,.0f}€/m² (DVF 2024). "
                f"{'Coût foncier élevé — prévoir surface optimisée ou local commercial existant.' if prix_moy > 7000 else 'Coût foncier modéré — opportunités de surfaces disponibles.' if prix_moy > 4000 else 'Coût foncier accessible — conditions favorables à l implantation.'}",
                S_reco_b
            ),
        ],
        [
            Paragraph("🎯 Recommandation", S_reco_t),
            Paragraph(
                f"Zone prioritaire recommandée : <b>{top1['nom_iris']}</b> "
                f"(Score {top1['score_final']:.0f}/100, RF {top1['rf_score']:.0f}/100). "
                f"Profil optimal : {int(top1['nb_concurrents_1km'])} concurrents dans 1km, "
                f"revenu médian {int(top1['revenu_median']):,}€, "
                f"prix m² {int(top1['prix_m2_median']):,}€.",
                S_reco_b
            ),
        ],
    ]

    for icon_row in reco_data:
        reco_t = Table([icon_row], colWidths=[4*cm, 13.4*cm])
        reco_t.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), white),
            ("LINEAFTER",   (0,0),(0,0),   0.5, HexColor("#E5E7EB")),
            ("LINEBEFORE",  (0,0),(0,0),   3,   ACCENT),
            ("PADDING",     (0,0),(-1,-1), 8),
            ("VALIGN",      (0,0),(-1,-1), "TOP"),
            ("TOPPADDING",  (0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ]))
        story.append(reco_t)
        story.append(Spacer(1, 0.12*cm))

    story.append(Spacer(1, 0.3*cm))

    # ── TABLEAU IRIS ──────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB"), spaceAfter=6))
    story.append(Paragraph(f"TOUS LES IRIS — {commune.upper()}", S_sec))

    thead = [
        Paragraph('<font size="7"><b>IRIS</b></font>', S_body),
        Paragraph('<font size="7"><b>SCORE FINAL</b></font>', S_body),
        Paragraph('<font size="7"><b>SITESCORE</b></font>', S_body),
        Paragraph('<font size="7"><b>RF SCORE</b></font>', S_body),
        Paragraph('<font size="7"><b>CONC. 1KM</b></font>', S_body),
        Paragraph('<font size="7"><b>REVENU €</b></font>', S_body),
        Paragraph('<font size="7"><b>PRIX M²</b></font>', S_body),
    ]
    tdata = [thead]
    for _, row in df_commune.head(20).iterrows():
        sc = row["score_final"]
        color = "#1A3557" if sc>=65 else "#2E6DA4" if sc>=55 else "#3B82F6" if sc>=45 else "#6B7280"
        tdata.append([
            Paragraph(f'<font size="8">{str(row["nom_iris"])[:28]}</font>', S_body),
            Paragraph(f'<font size="9" color="{color}"><b>{sc:.0f}</b></font>', S_body),
            Paragraph(f'<font size="8">{row["sitescore"]:.0f}</font>', S_body),
            Paragraph(f'<font size="8" color="#3B82F6">{row["rf_score"]:.0f}</font>', S_body),
            Paragraph(f'<font size="8">{int(row["nb_concurrents_1km"])}</font>', S_body),
            Paragraph(f'<font size="8">{int(row["revenu_median"]):,}€</font>', S_body),
            Paragraph(f'<font size="8">{int(row["prix_m2_median"]):,}€</font>', S_body),
        ])

    full_t = Table(tdata, colWidths=[5*cm, 2*cm, 2*cm, 2*cm, 1.8*cm, 2.2*cm, 2.4*cm])
    full_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  HexColor("#1A3557")),
        ("TEXTCOLOR",     (0,0),(-1,0),  white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  7),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, HexColor("#F8FAFF")]),
        ("PADDING",       (0,0),(-1,-1), 5),
        ("LINEBELOW",     (0,0),(-1,0),  0.5, HexColor("#2E6DA4")),
        ("GRID",          (0,1),(-1,-1), 0.3, HexColor("#E5E7EB")),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(full_t)
    story.append(Spacer(1, 0.4*cm))

    # ── MÉTHODO ───────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB"), spaceAfter=4))
    story.append(Paragraph("MÉTHODOLOGIE", S_sec))
    story.append(Paragraph(
        "Le Score Final combine le SiteScore (règles expertes pondérées : revenu 22%, densité 18%, concurrence 22%, "
        "accessibilité 18%, potentiel CA 10%, foncier 10%) et le RF Score (Random Forest entraîné sur 4070 IRIS IDF, "
        "accuracy 68%). Sources : IGN IRIS 2024 · INSEE FILOSOF · OSM · DVF 2024 · API BAN.",
        S_body
    ))

    # ── FOOTER ────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB"), spaceAfter=6))
    story.append(Paragraph(
        f"SiteScore · Massamba DIENG · Chargé d'études Géomarketing · 2026 · "
        f"massamba1806.github.io · massdieng1806@gmail.com",
        S_footer
    ))

    doc.build(story)
    print(f"✅ PDF : {output_path}")
    return output_path


if __name__ == "__main__":
    generate_pdf("Montreuil")