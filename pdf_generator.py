"""
pdf_generator.py
================
Génère un rapport PDF professionnel à partir d'une simulation Quant Terminal.
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)


# ==========================================
# Palette Quant Terminal
# ==========================================
PRIMARY = HexColor("#1a365d")
ACCENT  = HexColor("#319795")
SUCCESS = HexColor("#2f855a")
DANGER  = HexColor("#c53030")
MUTED   = HexColor("#718096")
BORDER  = HexColor("#e2e8f0")
LIGHT   = HexColor("#f7fafc")


def _styles():
    """Retourne les styles personnalisés du rapport."""
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "TitleQT", parent=base["Title"],
            fontName="Helvetica-Bold", fontSize=24,
            textColor=PRIMARY, alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleQT", parent=base["Normal"],
            fontName="Helvetica", fontSize=10,
            textColor=MUTED, alignment=TA_CENTER,
            spaceAfter=20,
        ),
        "h1": ParagraphStyle(
            "H1QT", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=15,
            textColor=PRIMARY, spaceBefore=14, spaceAfter=8,
            borderPadding=4,
        ),
        "h2": ParagraphStyle(
            "H2QT", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=12,
            textColor=PRIMARY, spaceBefore=10, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyQT", parent=base["Normal"],
            fontName="Helvetica", fontSize=10,
            textColor=HexColor("#2d3748"),
            alignment=TA_JUSTIFY, leading=14, spaceAfter=8,
        ),
        "tag": ParagraphStyle(
            "TagQT", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=8,
            textColor=MUTED, alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "scenario": ParagraphStyle(
            "ScenarioQT", parent=base["Normal"],
            fontName="Helvetica-Oblique", fontSize=11,
            textColor=HexColor("#2d3748"),
            alignment=TA_JUSTIFY, leading=15,
            leftIndent=10, rightIndent=10,
            spaceBefore=4, spaceAfter=10,
            borderColor=ACCENT, borderWidth=0,
            borderPadding=10, backColor=LIGHT,
        ),
    }
    return styles


def _table_metriques(metriques):
    """Tableau des 4 métriques de risque."""
    data = [
        ["Indicateur", "Valeur"],
        ["Volatilité annualisée", f"{metriques['vol_ann']:.2f} %"],
        ["Sharpe Ratio", f"{metriques['sharpe']:.2f}"],
        ["Max Drawdown", f"-{metriques['max_dd']:.2f} %"],
        ["VaR 95% (1 jour)", f"{metriques['var_95']:.2f} %"],
    ]
    t = Table(data, colWidths=[8 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ALIGN",       (1, 0), (1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",        (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    return t


def _table_macro(chocs):
    """Tableau des chocs macro IA."""
    macro = chocs.get("macro", {})
    data = [
        ["Indicateur macro", "Estimation IA"],
        ["Impact sur l'inflation", f"{macro.get('inflation', 0):+.2f} %"],
        ["Variation des taux directeurs", f"{macro.get('taux_directeurs', 0):+.2f} %"],
    ]
    t = Table(data, colWidths=[8 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ALIGN",       (1, 0), (1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",        (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    return t


def _table_perfs(perf_df):
    """Tableau de performance par actif."""
    data = [["Actif", "Performance (%)"]]
    rows_colors = []
    for _, row in perf_df.iterrows():
        perf = row['Performance (%)']
        data.append([row['Actif'], f"{perf:+.2f} %"])
        rows_colors.append(perf)

    t = Table(data, colWidths=[9 * cm, 4 * cm])

    style = [
        ("BACKGROUND",  (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ALIGN",       (1, 0), (1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]
    for i, perf in enumerate(rows_colors, start=1):
        if perf >= 0:
            style.append(("TEXTCOLOR", (1, i), (1, i), SUCCESS))
        else:
            style.append(("TEXTCOLOR", (1, i), (1, i), DANGER))
        style.append(("FONTNAME", (1, i), (1, i), "Helvetica-Bold"))

    t.setStyle(TableStyle(style))
    return t


def _table_portefeuille(allocations_finales, capital_initial, valeur_finale):
    """Tableau du détail du portefeuille."""
    data = [["Actif", "Poids", "Investi", "Final", "Performance"]]
    for ligne in allocations_finales:
        couleur_perf = SUCCESS if ligne["rendement"] >= 0 else DANGER
        data.append([
            ligne["nom"],
            f"{ligne['poids']*100:.1f}%",
            f"{ligne['investi']:,.0f} €".replace(",", " "),
            f"{ligne['final']:,.0f} €".replace(",", " "),
            f"{ligne['rendement']*100:+.2f} %",
        ])

    t = Table(data, colWidths=[5*cm, 2*cm, 3*cm, 3*cm, 3*cm])

    style = [
        ("BACKGROUND",  (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ("ALIGN",       (0, 0), (0, -1), "LEFT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]
    # Colorer la colonne Performance
    for i, ligne in enumerate(allocations_finales, start=1):
        couleur = SUCCESS if ligne["rendement"] >= 0 else DANGER
        style.append(("TEXTCOLOR", (4, i), (4, i), couleur))
        style.append(("FONTNAME", (4, i), (4, i), "Helvetica-Bold"))

    t.setStyle(TableStyle(style))
    return t


def _bilan_box(capital, valeur_finale):
    """Encart de bilan final coloré."""
    gain = valeur_finale - capital
    perf = (gain / capital) * 100 if capital > 0 else 0
    couleur = SUCCESS if gain >= 0 else DANGER

    data = [[
        f"Capital initial\n{capital:,.0f} €".replace(",", " "),
        f"Valeur finale\n{valeur_finale:,.0f} €".replace(",", " "),
        f"Performance\n{perf:+.2f} %",
    ]]
    t = Table(data, colWidths=[5*cm, 5*cm, 5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), couleur),
        ("TEXTCOLOR",   (0, 0), (-1, -1), white),
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 12),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
    ]))
    return t


def generer_rapport_pdf(simu, params, metriques, allocations_finales,
                         valeur_finale, type_rapport="Simulation", analyse_senior=None):
    """
    Génère un rapport PDF complet et retourne les bytes.

    Paramètres :
    - simu : dict avec scenario, chocs_ia, perf_df
    - params : dict avec capital, profil, actifs_sim, duree, etc.
    - metriques : dict avec vol_ann, sharpe, max_dd, var_95
    - allocations_finales : liste de dicts {nom, poids, investi, final, rendement}
    - valeur_finale : float
    - type_rapport : "Simulation" ou "Backtest"
    - analyse_senior : str optionnelle, analyse approfondie générée par l'IA
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Rapport Quant Terminal",
        author="Quant Terminal",
    )
    styles = _styles()
    story = []

    # ---- En-tête ----
    story.append(Paragraph(
        f'<font color="#319795">◆</font> QUANT TERMINAL',
        styles["title"]
    ))
    story.append(Paragraph(
        f"Rapport d'analyse · {type_rapport} · {datetime.now().strftime('%d %B %Y · %H:%M')}",
        styles["subtitle"]
    ))

    # ---- Scénario ----
    story.append(Paragraph("Scénario analysé", styles["h1"]))
    story.append(Paragraph(simu["scenario"], styles["scenario"]))

    # ---- Paramètres de simulation ----
    story.append(Paragraph("Paramètres de la simulation", styles["h2"]))
    params_text = (
        f"<b>Capital initial :</b> {params['capital']:,.0f} €<br/>"
        f"<b>Profil d'investisseur :</b> {params['profil']}<br/>"
        f"<b>Horizon :</b> {params.get('duree', 'N/A')} jours de cotation<br/>"
        f"<b>Nombre d'actifs analysés :</b> {len(params['actifs_sim'])}<br/>"
    ).replace(",", " ")
    if params.get("mc"):
        params_text += "<b>Mode Monte-Carlo :</b> activé (50 simulations)<br/>"
    if params.get("prix_reels"):
        params_text += "<b>Prix initiaux :</b> Yahoo Finance (temps réel)<br/>"
    if params.get("calib") and simu.get("chocs_ia", {}).get("evenement_reference"):
        params_text += f"<b>Calibration historique IA :</b> {simu['chocs_ia']['evenement_reference']}<br/>"
    story.append(Paragraph(params_text, styles["body"]))

    # ---- Synthèse macro IA ----
    chocs = simu.get("chocs_ia", {})
    if chocs.get("explication_courte"):
        story.append(Paragraph("Synthèse macro de l'IA", styles["h2"]))
        story.append(Paragraph(
            f'<i>{chocs["explication_courte"]}</i>',
            styles["body"]
        ))

    # ---- Chocs macro ----
    if chocs.get("macro"):
        story.append(Paragraph("Impacts macro-économiques estimés", styles["h2"]))
        story.append(_table_macro(chocs))
        story.append(Spacer(1, 12))

    # ---- Bilan portefeuille ----
    story.append(Paragraph("Bilan du portefeuille", styles["h1"]))
    story.append(_bilan_box(params["capital"], valeur_finale))
    story.append(Spacer(1, 14))

    # ---- Métriques de risque ----
    story.append(Paragraph("Métriques de risque", styles["h2"]))
    story.append(Paragraph(
        "Indicateurs institutionnels utilisés par les gérants de fonds professionnels.",
        styles["body"]
    ))
    story.append(_table_metriques(metriques))
    story.append(Spacer(1, 12))

    # ---- Composition complète du portefeuille ----
    story.append(Spacer(1, 16))
    story.append(Paragraph("Composition détaillée du portefeuille", styles["h1"]))
    story.append(Paragraph(
        f"Décomposition de votre portefeuille de {params['capital']:,.0f} € selon le profil "
        f"<b>{params['profil']}</b>. Chaque ligne montre l'allocation, le montant investi initialement, "
        f"la valeur finale et la performance individuelle de l'actif sur la période simulée.".replace(",", " "),
        styles["body"]
    ))
    story.append(Spacer(1, 8))
    story.append(_table_portefeuille(allocations_finales, params["capital"], valeur_finale))
    story.append(Spacer(1, 14))

    # ---- Performance par actif ----
    story.append(Paragraph("Performance par actif (tous les actifs analysés)", styles["h2"]))
    story.append(Paragraph(
        "Performance brute de chaque actif simulé indépendamment du portefeuille. "
        "Permet d'identifier quelles classes d'actifs ont le mieux ou le moins bien réagi au scénario.",
        styles["body"]
    ))
    story.append(Spacer(1, 6))
    story.append(_table_perfs(simu["perf_df"]))
    story.append(Spacer(1, 14))

    # ---- ANALYSE SENIOR (NOUVEAU) ----
    if analyse_senior:
        story.append(Spacer(1, 18))
        story.append(Paragraph("Analyse approfondie de l'analyste senior", styles["h1"]))
        story.append(Paragraph(
            "<i>Rapport rédigé par l'analyste financier IA, dans le style d'un professionnel "
            "institutionnel d'une banque d'investissement.</i>",
            styles["body"]
        ))
        story.append(Spacer(1, 10))

        # Convertir le markdown simple en HTML pour reportlab
        analyse_html = analyse_senior.replace("**", "@@@")
        # Alternance @@@ pour <b></b>
        parts = analyse_html.split("@@@")
        analyse_formatted = ""
        for i, part in enumerate(parts):
            if i % 2 == 1:
                analyse_formatted += f"<b>{part}</b>"
            else:
                analyse_formatted += part
        # Sauts de ligne en doubles paragraphes
        for paragraphe in analyse_formatted.split("\n\n"):
            paragraphe = paragraphe.strip().replace("\n", "<br/>")
            if paragraphe:
                story.append(Paragraph(paragraphe, styles["body"]))
                story.append(Spacer(1, 6))

    # ---- Note méthodologique ----
    story.append(Spacer(1, 14))
    story.append(Paragraph("Note méthodologique", styles["h2"]))
    note = (
        "Quant Terminal est un outil pédagogique. Les simulations utilisent un mouvement brownien "
        "géométrique calibré par une intelligence artificielle qui interprète le scénario et estime "
        "les chocs sur chaque classe d'actifs. Les volatilités sont calculées à partir des données "
        "historiques Yahoo Finance sur 12 mois. Les métriques de risque (Volatilité annualisée, Sharpe Ratio, "
        "Max Drawdown, VaR 95%) sont calculées selon les standards institutionnels. "
        "Limites connues : volatilités supposées constantes, actifs traités indépendamment, "
        "pas de prise en compte des coûts de transaction. Outil non destiné à un usage professionnel "
        "en l'état."
    )
    story.append(Paragraph(note, styles["body"]))

    # ---- Pied de page ----
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f'<font color="#718096"><i>Rapport généré automatiquement par Quant Terminal · '
        f'Université Paris Nanterre · MIASHS</i></font>',
        ParagraphStyle("Footer", parent=styles["body"],
                       alignment=TA_CENTER, fontSize=8, textColor=MUTED)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()