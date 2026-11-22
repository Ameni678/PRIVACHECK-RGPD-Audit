from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.units import mm
from xml.sax.saxutils import escape

def generate_pdf(result, lang="fr"):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#17365D"), spaceAfter=12))
    story = []
    fr = lang == "fr"
    de = lang == "de"
    ar = lang == "ar"
    story.append(Paragraph("PRIVACHECK AI", styles["CoverTitle"]))
    report_title = "Rapport indicatif d'audit documentaire RGPD" if fr else "Indicative GDPR document screening report"
    if de: report_title = "Indikativer DSGVO-Dokumentenprüfbericht"
    if ar: report_title = "تقرير فحص وثائق حماية البيانات" 
    story.append(Paragraph(report_title, styles["Heading2"]))
    story.append(Spacer(1,8))
    story.append(Paragraph(f"<b>{'Document' if fr else 'Document'}:</b> {escape(result['title'])}", styles["BodyText"]))
    story.append(Paragraph(f"<b>{'Date' if fr else 'Date'}:</b> {escape(result['created_at'])}", styles["BodyText"]))
    story.append(Paragraph(f"<b>{'Indicateur documentaire' if fr else 'Documentary indicator'}:</b> {result['score']:.1f}%", styles["BodyText"]))
    story.append(Spacer(1,12))
    story.append(Paragraph("Résumé" if fr else "Zusammenfassung" if de else "الملخص" if ar else "Summary", styles["Heading2"]))
    story.append(Paragraph(escape(result["summary"]), styles["BodyText"]))
    story.append(Spacer(1,10))
    story.append(Paragraph("Résultats par critère" if fr else "Results by criterion", styles["Heading2"]))
    data = [["Critère" if fr else "Kriterium" if de else "المعيار" if ar else "Criterion", "Résultat" if fr else "Ergebnis" if de else "النتيجة" if ar else "Result", "Référence" if fr else "Referenz" if de else "المرجع" if ar else "Reference"]]
    for x in result["details"]:
        data.append([Paragraph(escape(x["criterion"]),styles["BodyText"]),Paragraph(escape(x["status"]),styles["BodyText"]),Paragraph(escape(x["reference"]),styles["BodyText"])])
    table = Table(data, colWidths=[68*mm,54*mm,48*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17365D")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#B8C4D1")),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F2F5F8")]),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)
    ]))
    story.append(table)
    story.append(Spacer(1,12))
    story.append(Paragraph("Recommandations générales" if fr else "Allgemeine Empfehlungen" if de else "توصيات عامة" if ar else "General recommendations", styles["Heading2"]))
    for rec in result["recommendations"]:
        story.append(Paragraph("• " + escape(rec), styles["BodyText"]))
        story.append(Spacer(1,4))
    story.append(Spacer(1,12))
    disclaimer = ("Limite : cet outil réalise un repérage documentaire automatisé. Il ne constitue ni une certification, ni un avis juridique, ni un audit complet de l'organisation."
                  if fr else "Limitation: this tool performs automated document screening. It is not a certification, legal opinion or full organisational audit.")
    story.append(Paragraph("<b>" + escape(disclaimer) + "</b>", styles["Italic"]))
    doc.build(story)
    return buf.getvalue()
