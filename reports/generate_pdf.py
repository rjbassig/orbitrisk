"""Build the downloadable report from the reviewed, public Markdown content."""
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

root = Path(__file__).parent
output = root / "orbitrisk_research.pdf"
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleDark", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=34, textColor=HexColor("#102b3d"), spaceAfter=18))
styles.add(ParagraphStyle(name="HeadingDark", parent=styles["Heading2"], fontName="Helvetica-Bold", textColor=HexColor("#174d68"), spaceBefore=16, spaceAfter=7))
styles.add(ParagraphStyle(name="BodyDark", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.2, leading=15, textColor=HexColor("#17232a"), spaceAfter=8))
story = [Paragraph("ORBITRISK", styles["TitleDark"]), Paragraph("Satellite Conjunction Risk Modeling", styles["Heading1"]), Paragraph("Applied orbital analytics / research release 0.1", styles["BodyDark"]), Spacer(1, .18*inch)]
for raw in (root / "orbitrisk_research.md").read_text().splitlines():
    if raw.startswith("# "): continue
    if raw.startswith("## "): story.append(Paragraph(raw[3:], styles["HeadingDark"])); continue
    if not raw.strip(): continue
    story.append(Paragraph(raw, styles["BodyDark"]))
SimpleDocTemplate(str(output), pagesize=letter, rightMargin=.78*inch, leftMargin=.78*inch, topMargin=.72*inch, bottomMargin=.72*inch, title="OrbitRisk Research Report", author="Randall Bassig").build(story)
print(output)
