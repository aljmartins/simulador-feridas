from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from datetime import datetime

def gerar_pdf_relatorio(
    path,
    caso: dict,
    resposta_estudante: str,
    plano_ideal: str,
    feedback: str,
):
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>RELATÓRIO DE AVALIAÇÃO – FERIDAS CRÔNICAS</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>1. Caso Clínico</b>", styles["Heading2"]))
    for k, v in caso.items():
        story.append(Paragraph(f"<b>{k.capitalize()}:</b> {v}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>2. Resposta do Estudante</b>", styles["Heading2"]))
    story.append(Paragraph(resposta_estudante.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>3. Plano Ideal (Core TIME)</b>", styles["Heading2"]))
    story.append(Paragraph(plano_ideal.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>4. Feedback Automatizado</b>", styles["Heading2"]))
    story.append(Paragraph(feedback.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(story)
