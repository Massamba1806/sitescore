import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

def generate_pdf(commune: str, output_path: str = None):

    # ── Charge données ───────────────────────
    df = pd.read_csv("data/exports/sitescore_idf.csv")
    df_commune = df[
        df["commune"].str.contains(commune, case=False, na=False)
    ].sort_values("score_final", ascending=False)

    if df_commune.empty:
        print(f"❌ Aucun résultat pour '{commune}'")
        return

    top5 = df_commune.head(5)

    if output_path is None:
        os.makedirs("data/exports/pdf", exist_ok=True)
        output_path = f"data/exports/pdf/SiteScore_{commune.replace(' ','_')}.pdf"

    # ── Couleurs ─────────────────────────────
    DARK       = HexColor("#0A0E1A")
    DARK2      = HexColor("#0D1117")
    BORDER     = HexColor("#1E2D3D")
    CYAN       = HexColor("#00D4FF")
    GREEN      = HexColor("#00FF88")
    YELLOW     = HexColor("#FFD700")
    ORANGE     = HexColor("#FF6B35")
    PURPLE     = HexColor("#C084FC")
    LIGHT      = HexColor("#E0E6ED")
    MUTED      = HexColor("#8B9BB4")
    DARK_MUTED = HexColor("#4A5568")

    RANK_COLORS = [CYAN, GREEN, YELLOW, ORANGE, PURPLE]

    # ── Document ─────────────────────────────
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()

    # Styles custom
    style_title = ParagraphStyle(
        "title",
        fontSize=28, fontName="Helvetica-Bold",
        textColor=white, alignment=TA_LEFT,
        spaceAfter=4,
    )
    style_subtitle = ParagraphStyle(
        "subtitle",
        fontSize=11, fontName="Helvetica",
        textColor=MUTED, alignment=TA_LEFT,
        spaceAfter=0,
    )
    style_eyebrow = ParagraphStyle(
        "eyebrow",
        fontSize=8, fontName="Helvetica-Bold",
        textColor=DARK_MUTED, alignment=TA_LEFT,
        spaceAfter=4, leading=10,
    )
    style_section = ParagraphStyle(
        "section",
        fontSize=8, fontName="Helvetica-Bold",
        textColor=DARK_MUTED, alignment=TA_LEFT,
        spaceAfter=8, leading=10,
    )
    style_body = ParagraphStyle(
        "body",
        fontSize=9, fontName="Helvetica",
        textColor=MUTED, alignment=TA_LEFT,
        spaceAfter=4, leading=14,
    )
    style_rank = ParagraphStyle(
        "rank",
        fontSize=11, fontName="Helvetica-Bold",
        textColor=LIGHT, alignment=TA_LEFT,
        spaceAfter=2,
    )
    style_footer = ParagraphStyle(
        "footer",
        fontSize=7, fontName="Helvetica",
        textColor=DARK_MUTED, alignment=TA_CENTER,
    )

    story = []

    # ── HEADER ───────────────────────────────
    header_data = [[
        Paragraph(
            f'<font color="#4A5568" size="8">LOCATION INTELLIGENCE REPORT</font><br/>'
            f'<font color="#E0E6ED" size="26"><b>{commune.upper()}</b></font><br/>'
            f'<font color="#8B9BB4" size="10">Île-de-France · Analyse d\'implantation commerciale</font>',
            styles["Normal"]
        ),
        Paragraph(
            f'<font color="#00D4FF" size="28"><b>SITE</b></font>'
            f'<font color="#E0E6ED" size="28"><b>SCORE</b></font><br/>'
            f'<font color="#4A5568" size="7">RETAIL LOCATION INTELLIGENCE</font>',
            ParagraphStyle("logo", alignment=TA_RIGHT,
                          fontSize=28, fontName="Helvetica-Bold")
        )
    ]]
    header_table = Table(header_data, colWidths=[12*cm, 6*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), DARK2),
        ("PADDING",      (0,0), (-1,-1), 16),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), 8),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # ── KPI ROW ──────────────────────────────
    top1 = top5.iloc[0]
    kpi_data = [[
        Paragraph(f'<font color="#00D4FF" size="24"><b>{top1["score_final"]:.0f}</b></font><br/>'
                  f'<font color="#4A5568" size="7">SCORE FINAL</font>', styles["Normal"]),
        Paragraph(f'<font color="#00FF88" size="24"><b>{top1["sitescore"]:.0f}</b></font><br/>'
                  f'<font color="#4A5568" size="7">SITESCORE</font>', styles["Normal"]),
        Paragraph(f'<font color="#FFD700" size="24"><b>{top1["rf_score"]:.0f}</b></font><br/>'
                  f'<font color="#4A5568" size="7">RF SCORE</font>', styles["Normal"]),
        Paragraph(f'<font color="#FF6B35" size="24"><b>{int(top1["nb_concurrents_1km"])}</b></font><br/>'
                  f'<font color="#4A5568" size="7">CONCURRENTS 1KM</font>', styles["Normal"]),
        Paragraph(f'<font color="#C084FC" size="20"><b>{int(top1["prix_m2_median"]):,}€</b></font><br/>'
                  f'<font color="#4A5568" size="7">PRIX M² DVF</font>', styles["Normal"]),
    ]]
    kpi_table = Table(kpi_data, colWidths=[3.6*cm]*5)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK2),
        ("PADDING",    (0,0), (-1,-1), 12),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LINEAFTER",  (0,0), (3,0), 0.5, BORDER),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.4*cm))

    # ── TOP 5 ────────────────────────────────
    story.append(Paragraph("TOP 5 — EMPLACEMENTS RECOMMANDÉS", style_section))

    MEDALS = ["#1 OPTIMAL", "#2 EXCELLENT", "#3 BON", "#4 CORRECT", "#5 ACCEPTABLE"]

    for i, (_, row) in enumerate(top5.iterrows()):
        color = RANK_COLORS[i]
        medal = MEDALS[i]

        concurrents = int(row['nb_concurrents_1km'])
        if concurrents <= 2:   conc_label = "FAIBLE"
        elif concurrents <= 5: conc_label = "MODÉRÉ"
        else:                  conc_label = "ÉLEVÉ"

        row_data = [[
            Paragraph(
                f'<font size="8"><b>{medal}</b></font><br/>'
                f'<font size="12"><b>{row["nom_iris"]}</b></font><br/>'
                f'<font size="8" color="#8B9BB4">{row["commune"]} · Dept {row["dept"]}</font><br/>'
                f'<font size="8" color="#8B9BB4">'
                f'Concurrents 1km : {concurrents} ({conc_label}) | '
                f'Revenu : {int(row["revenu_median"]):,}€ | '
                f'Prix m² : {int(row["prix_m2_median"]):,}€'
                f'</font>',
                styles["Normal"]
            ),
            Paragraph(
                f'<font size="28"><b>{row["score_final"]:.0f}</b></font><br/>'
                f'<font size="8" color="#4A5568">/100</font><br/>'
                f'<font size="8" color="#4A5568">RF:{row["rf_score"]:.0f}</font>',
                ParagraphStyle("score_cell", alignment=TA_CENTER,
                               fontSize=28, fontName="Helvetica-Bold")
            ),
        ]]

        rank_table = Table(row_data, colWidths=[14*cm, 4*cm])
        rank_table.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), DARK2),
            ("PADDING",      (0,0), (-1,-1), 12),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("LINEAFTER",    (0,0), (0,0), 0.5, BORDER),
            ("LINEAFTER",    (0,0), (-1,-1), 3, color),
        ]))
        story.append(rank_table)
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.3*cm))

    # ── TABLEAU COMPLET ───────────────────────
    story.append(Paragraph(f"TOUS LES IRIS — {commune.upper()}", style_section))

    table_data = [[
        Paragraph('<font size="7" color="#4A5568"><b>IRIS</b></font>', styles["Normal"]),
        Paragraph('<font size="7" color="#4A5568"><b>SCORE FINAL</b></font>', styles["Normal"]),
        Paragraph('<font size="7" color="#4A5568"><b>SITESCORE</b></font>', styles["Normal"]),
        Paragraph('<font size="7" color="#4A5568"><b>RF SCORE</b></font>', styles["Normal"]),
        Paragraph('<font size="7" color="#4A5568"><b>CONC. 1KM</b></font>', styles["Normal"]),
        Paragraph('<font size="7" color="#4A5568"><b>REVENU €</b></font>', styles["Normal"]),
        Paragraph('<font size="7" color="#4A5568"><b>PRIX M²</b></font>', styles["Normal"]),
    ]]

    for _, row in df_commune.head(20).iterrows():
        table_data.append([
            Paragraph(f'<font size="8" color="#E0E6ED">{row["nom_iris"][:25]}</font>',
                     styles["Normal"]),
            Paragraph(f'<font size="9" color="#00D4FF"><b>{row["score_final"]:.0f}</b></font>',
                     styles["Normal"]),
            Paragraph(f'<font size="8" color="#8B9BB4">{row["sitescore"]:.0f}</font>',
                     styles["Normal"]),
            Paragraph(f'<font size="8" color="#FFD700">{row["rf_score"]:.0f}</font>',
                     styles["Normal"]),
            Paragraph(f'<font size="8" color="#FF6B35">{int(row["nb_concurrents_1km"])}</font>',
                     styles["Normal"]),
            Paragraph(f'<font size="8" color="#8B9BB4">{int(row["revenu_median"]):,}€</font>',
                     styles["Normal"]),
            Paragraph(f'<font size="8" color="#C084FC">{int(row["prix_m2_median"]):,}€</font>',
                     styles["Normal"]),
        ])

    full_table = Table(table_data,
                       colWidths=[5.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2.5*cm, 2*cm])
    full_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  BORDER),
        ("BACKGROUND",   (0,1), (-1,-1), DARK2),
        ("PADDING",      (0,0), (-1,-1), 6),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [DARK2, HexColor("#0F1621")]),
        ("LINEBELOW",    (0,0), (-1,0),  0.5, BORDER),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(full_table)
    story.append(Spacer(1, 0.5*cm))

    # ── MÉTHODOLOGIE ─────────────────────────
    story.append(Paragraph("MÉTHODOLOGIE", style_section))
    story.append(Paragraph(
        "Le Score Final combine le SiteScore (règles expertes pondérées) et le RF Score "
        "(Random Forest entraîné sur 4 070 IRIS IDF). "
        "6 features : revenus INSEE · densité population · concurrence OSM · "
        "accessibilité · potentiel CA · prix immobilier DVF 2024.",
        style_body
    ))

    # ── FOOTER ───────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=BORDER, spaceAfter=8))
    story.append(Paragraph(
        f"SiteScore · Massamba DIENG · Chargé d'études Géomarketing · 2026 · "
        f"Python · PostGIS · Random Forest · DVF · OSM · INSEE",
        style_footer
    ))

    # ── Build ─────────────────────────────────
    doc.build(story)
    print(f"✅ PDF généré : {output_path}")
    return output_path


if __name__ == "__main__":
    commune = "Montreuil"
    generate_pdf(commune)
    print(f"\n🎉 Rapport PDF SiteScore — {commune} généré !")