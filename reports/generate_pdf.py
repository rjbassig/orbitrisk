"""Build the downloadable report from the reviewed, public Markdown content."""
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.graphics.shapes import Drawing, Rect, String
import json

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
snapshot = json.loads((root.parent / "web/public/research/orbitrisk-snapshot.json").read_text())
events = snapshot["screen"]["nearest_approaches"][:8]
drawing = Drawing(500, max(120, 24 + len(events) * 24))
for index, event in enumerate(reversed(events)):
    y = 18 + index * 24
    value = float(event["miss_distance_km"])
    width = max(2, min(300, value / max(float(events[0]["miss_distance_km"]), 1) * 300))
    label = f'{event["primary"]["name"]} x {event["secondary"]["name"]}'[:38]
    drawing.add(String(0, y + 4, label, fontName="Helvetica", fontSize=7, fillColor=HexColor("#42515b")))
    drawing.add(Rect(210, y, width, 12, fillColor=HexColor("#6d9f91"), strokeColor=None))
    drawing.add(String(216 + width, y + 3, f'{value:.2f} km', fontName="Helvetica", fontSize=7, fillColor=HexColor("#17232a")))
story.extend([Spacer(1, .12*inch), Paragraph("Nearest geometric approaches from the verified Resource catalog", styles["HeadingDark"]), drawing])
SimpleDocTemplate(str(output), pagesize=letter, rightMargin=.78*inch, leftMargin=.78*inch, topMargin=.72*inch, bottomMargin=.72*inch, title="OrbitRisk Research Report", author="Randall Bassig").build(story)
print(output)
