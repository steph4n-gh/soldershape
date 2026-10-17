import csv
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, NextPageTemplate,
                               PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)
from svglib.svglib import svg2rlg

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "force_lab"
OUTPUT = ROOT / "output/pdf/soldershape-force-lab-handoff.pdf"
INK = colors.HexColor("#143943")
ACCENT = colors.HexColor("#94502c")


def inline(text):
    text = escape(text)
    text = re.sub(r"\[([^]]+)\]\((https?://[^ )]+)\)", r'<link href="\2" color="#94502c">\1</link>', text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r'<b>\1</b>', text)
    return text


def markdown(path, styles):
    flow = []
    paragraph = []
    code = False
    table = []

    def flush():
        if paragraph:
            flow.append(Paragraph(inline(" ".join(paragraph)), styles["BodyText"]))
            paragraph.clear()
        if table:
            width = A4[0] - 84
            columns = max(map(len, table))
            cells = [[Paragraph(inline(cell), styles["Cell"]) for cell in row] for row in table]
            item = Table(cells, colWidths=[width / columns] * columns, repeatRows=1, hAlign="LEFT")
            item.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4efed")),
                                     ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                                     ("TOPPADDING", (0, 0), (-1, -1), 7),
                                     ("LINEBELOW", (0, 0), (-1, -1), .3, colors.HexColor("#c4d5d3"))]))
            flow.extend([item, Spacer(1, 10)])
            table.clear()

    for line in path.read_text().splitlines():
        if line.startswith("```"):
            flush()
            code = not code
        elif code:
            if line.strip():
                flow.append(Paragraph(escape(line), styles["CodeLine"]))
        elif line.startswith("|"):
            if not re.match(r"^\|[ :|\-]+\|$", line):
                if paragraph:
                    flush()
                table.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif not line.strip():
            flush()
        elif line.startswith("#"):
            flush()
            level = len(line) - len(line.lstrip("#"))
            flow.append(Paragraph(inline(line[level:].strip()), styles["Heading1" if level == 1 else "Heading2"]))
        elif re.match(r"^(\d+\.|[-*]) ", line):
            flush()
            flow.append(Paragraph(inline(line), styles["BulletText"]))
        else:
            if table:
                flush()
            paragraph.append(line.strip())
    flush()
    return flow


def footer(canvas, doc):
    width, height = canvas._pagesize
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.setFont("Vera-Bold", 8)
    canvas.drawString(42, height - 27, "SOLDERSHAPE  /  FORCE EXPERIMENT R1  /  QUOTATION ONLY")
    canvas.setFillColor(INK)
    canvas.setFont("Vera", 7)
    canvas.drawString(42, 23, "Not lab accepted. Not fabrication released. Physical force accuracy remains unqualified.")
    canvas.drawRightString(width - 42, 23, str(doc.page))
    canvas.restoreState()


def main():
    import reportlab
    font_dir = Path(reportlab.__file__).parent / "fonts"
    for name, filename in (("Vera", "Vera.ttf"), ("Vera-Bold", "VeraBd.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily("Vera", normal="Vera", bold="Vera-Bold", italic="Vera", boldItalic="Vera-Bold")
    styles = getSampleStyleSheet()
    for name in ("BodyText", "Heading1", "Heading2", "Title"):
        styles[name].fontName = "Vera-Bold" if name != "BodyText" else "Vera"
        styles[name].textColor = INK
    styles["BodyText"].fontSize = 9
    styles["BodyText"].leading = 13.5
    styles["BodyText"].spaceAfter = 7
    styles["Heading1"].fontSize = 18
    styles["Heading1"].leading = 23
    styles["Heading2"].fontSize = 12
    styles["Heading2"].leading = 16
    styles.add(ParagraphStyle("Cell", parent=styles["BodyText"], fontSize=7.5, leading=10, spaceAfter=0))
    styles.add(ParagraphStyle("CodeLine", fontName="Courier", fontSize=7, leading=10, spaceAfter=3,
                              textColor=INK, splitLongWords=True, alignment=TA_LEFT))
    styles.add(ParagraphStyle("BulletText", parent=styles["BodyText"], leftIndent=10, firstLineIndent=-10))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(str(OUTPUT), pagesize=A4, title="SolderShape matching force experiment",
                               author="SolderShape", leftMargin=42, rightMargin=42,
                               topMargin=48, bottomMargin=42)
    templates = []
    for name, size in (("portrait", A4), ("drawing", landscape(A4))):
        frame = Frame(42, 42, size[0] - 84, size[1] - 90, id=name, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        templates.append(PageTemplate(id=name, frames=[frame], pagesize=size, onPage=footer))
    document.addPageTemplates(templates)
    flow = [Spacer(1, 25), Paragraph("Matching molten-joint<br/>force experiment", styles["Title"]),
            Spacer(1, 15), Paragraph("A staged outside-lab quotation and commissioning package", styles["Heading2"]),
            Paragraph("200 µm circular rims · 150 µm held gap · 5 versus 7 nL · 40 and 120 µm offset", styles["BodyText"]),
            Spacer(1, 15), Paragraph("The question is whether independent physical observations can discriminate the predicted forces. Exact CAD, a native replay, and instrument resolution do not answer it.", styles["BodyText"]),
            Paragraph("Release state", styles["Heading2"]),
            Paragraph("Prepared for quote. Supplier-specific interfaces, contact-line observability, thermal integration, actual process inputs and the complete uncertainty budget require laboratory acceptance. No fabrication or purchase is authorized.", styles["BodyText"]),
            Paragraph("Read the editable sources and manifest with this handbook. The DXF artwork specifies a nominal thin-film boundary on glass. It is not ordinary PCB CAM or a qualified wetting process.", styles["BodyText"]),
            PageBreak()]
    for name in ("README.md", "RFQ.md", "PROCEDURE.md", "uncertainties.md", "ANALYSIS.md"):
        flow.extend(markdown(LAB / name, styles))
        flow.append(PageBreak())
    flow.append(Paragraph("Parts and instrumentation", styles["Heading1"]))
    with (LAB / "BOM.csv").open(newline="") as source:
        rows = list(csv.DictReader(source))
    for row in rows:
        heading = " · ".join(str(value) for key, value in list(row.items())[:3] if value)
        entries = [Paragraph(inline(heading), styles["Heading2"])]
        for key, value in list(row.items())[3:]:
            if value:
                entries.append(Paragraph(inline(key.replace("_", " ") + ". " + value), styles["BodyText"]))
        flow.extend(entries)
    drawings = sorted((LAB / "hardware").rglob("*.svg"))
    if not drawings:
        raise ValueError("No dimensioned mechanical SVG drawings were generated.")
    for path in drawings:
        flow.extend([NextPageTemplate("drawing"), PageBreak()])
        drawing = svg2rlg(str(path))
        if drawing is None:
            raise ValueError("Cannot render drawing " + str(path))
        width, height = landscape(A4)
        scale = min((width - 84) / drawing.width, (height - 100) / drawing.height)
        drawing.scale(scale, scale)
        drawing.width *= scale
        drawing.height *= scale
        flow.append(drawing)
    document.build(flow)
    print(OUTPUT)


if __name__ == "__main__":
    main()
