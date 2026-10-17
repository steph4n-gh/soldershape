import csv
from html import escape
import json
from pathlib import Path
import re
import sys

from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_boards import gerber

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "coupons"
NAVY = colors.HexColor("#142e45")
TEAL = colors.HexColor("#087e8b")
ORANGE = colors.HexColor("#b35a13")
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle("Text", fontName="Helvetica", fontSize=9, leading=13, spaceAfter=7, allowWidows=0, allowOrphans=0))
STYLES.add(ParagraphStyle("SmallText", parent=STYLES["Text"], fontSize=7.5, leading=10))
STYLES.add(ParagraphStyle("Command", fontName="Courier", fontSize=7, leading=10, spaceAfter=5, wordWrap="CJK"))
for name in ("Heading1", "Heading2", "Heading3"):
    STYLES[name].textColor = NAVY
    STYLES[name].spaceBefore = 12
    STYLES[name].keepWithNext = 1
STYLES["Heading1"].fontSize = 20
STYLES["Heading1"].leading = 24
STYLES["Heading2"].fontSize = 13
STYLES["Heading2"].leading = 17


def formatted(text):
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escape(text))


def paragraph(text, style="Text"):
    return Paragraph(formatted(text), STYLES[style])


def table(rows, widths):
    cells = [[paragraph(str(cell), "SmallText") for cell in row] for row in rows]
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5eef4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), .6, NAVY),
        ("LINEBELOW", (0, 1), (-1, -1), .25, colors.lightgrey),
    ]))
    return result


def board_drawing(spec):
    drawing = Drawing(504, 278)
    for name, origin, scale, copper in (
        ("carrier", (15, 30), 5.3, "F_Cu.gtl"),
        ("cap", (330, 75), 43, "B_Cu.gbl"),
    ):
        x0, y0 = origin
        width, height = spec[name]["width_mm"], spec[name]["height_mm"]
        xy = lambda x, y: (x0+x*scale, y0+(height-y)*scale)
        drawing.add(Rect(x0, y0, width*scale, height*scale, fillColor=colors.HexColor("#f4f7f7"), strokeColor=NAVY))
        mask = "F_Mask.gts" if name == "carrier" else "B_Mask.gbs"
        for region in gerber(HERE / "fabrication" / name / f"{name}-{mask}")[2]:
            xs, ys = zip(*region)
            x, y = xy(min(xs), max(ys))
            drawing.add(Rect(x, y, (max(xs)-min(xs))*scale, (max(ys)-min(ys))*scale,
                             fillColor=colors.HexColor("#dce6e7"), strokeColor=None))
        for x, y, shape, diameter in gerber(HERE / "fabrication" / name / f"{name}-{copper}")[0]:
            color = TEAL if diameter == .22 else ORANGE if diameter == .27 else NAVY
            px, py = xy(x, y)
            drawing.add(Circle(px, py, diameter*scale/2, fillColor=color, strokeColor=None))
        if name == "carrier":
            for site in spec["carrier"]["sites"]:
                x, y = xy(site["x_mm"], site["y_mm"]-3.8)
                drawing.add(String(x, y, site["site"]+" / "+site["arm"], textAnchor="middle", fontSize=8, fillColor=NAVY))
                x, y = xy(site["x_mm"]-2, site["y_mm"]-.75)
                drawing.add(String(x, y, "A1", textAnchor="end", fontSize=6.5, fillColor=NAVY))
            for x, y in ((4, 20), (36, 20)):
                px, py = xy(x, y)
                drawing.add(Circle(px, py, 1.6*scale, fillColor=colors.white, strokeColor=NAVY))
            drawing.add(String(x0, y0-15, "40 x 40 x 1.6 mm / F.Cu upward", fontSize=9, fillColor=NAVY))
        else:
            a, b, c = xy(.25, .25), xy(.7, .25), xy(.25, .7)
            for end in (b, c):
                drawing.add(Line(*a, *end, strokeColor=TEAL, strokeWidth=3))
            drawing.add(String(x0, y0-18, "3 x 3 x 0.8 mm / 20 mating pads", fontSize=9, fillColor=NAVY))
            drawing.add(String(x0, y0-32, "Outer face shown, looking through cap", fontSize=8, fillColor=NAVY))
            drawing.add(String(x0, y0-46, "L corner = A1. B.Cu faces downward.", fontSize=8, fillColor=NAVY))
    drawing.add(String(15, 262, "CARRIER / common top view", fontSize=10, fillColor=NAVY))
    drawing.add(String(330, 223, "CAP / same top-view axes", fontSize=10, fillColor=NAVY))
    drawing.add(String(15, 0, "Illustration from exported Gerber coordinates. Views use different scales. CAD controls dimensions.", fontSize=8, fillColor=NAVY))
    return drawing


def markdown(story, path):
    pending, code = [], False

    def flush():
        if pending:
            story.append(paragraph(" ".join(pending)))
            pending.clear()

    for line in path.read_text().splitlines():
        if line.startswith("```"):
            flush()
            code = not code
        elif code:
            story.append(paragraph(line, "Command"))
        elif line.startswith("#"):
            flush()
            level = len(line)-len(line.lstrip("#"))
            story.append(paragraph(line.lstrip("# "), "Heading1" if level == 1 else "Heading2"))
        elif not line.strip():
            flush()
        elif line.startswith("- ") or re.match(r"^\d+\. ", line):
            flush()
            story.append(paragraph(line))
        else:
            pending.append(line)
    flush()


def footer(canvas, doc):
    canvas.setStrokeColor(TEAL)
    canvas.line(42, 39, 570, 39)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(42, 26, "SS-C220-C270-R1 | Quote and pilot package | No physical results")
    canvas.drawRightString(570, 26, str(doc.page))


def main():
    spec = json.loads((HERE / "experiment.json").read_text())
    output = ROOT / "output/pdf/soldershape-lab-handoff.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    story = [paragraph("SolderShape physical coupon", "Heading1"),
             paragraph("220 versus 270 micrometer pads | Outside-laboratory handoff", "Heading2"),
             paragraph("Prepared for a quote and staged pilot. No parts ordered, no laboratory results, and no fabrication release. Obtain written DFM, material, assembly and metrology acceptance before work."),
             board_drawing(spec), Spacer(1, 10),
             paragraph("One controlled comparison", "Heading2"),
             paragraph("Compare two lower pad diameters with a common 280 micrometer upper pad, a 5 by 4 array at 0.5 mm pitch, graded Sn63Pb37 spheres and one fixed process. Preserve isolated pads, the common 2.8 by 2.3 mm mask opening, actual cap mass, both finished metal heights and one sphere per joint."),
             table([["Cohort", "Carriers / caps", "Purpose"],
                    ["Pilot", "3 / 12", "Three separate runs, six pairs. Qualify process and measurement precision."],
                    ["Confirmation", "6 / 24", "Three further runs, four pairs per run. Keep all attempts."],
                    ["Profile and spare", "1 / 4 and 2 / 8", "Dedicated temperature profiling and recorded contingencies."]], [100, 110, 294]),
             PageBreak(),
             paragraph("Assembly datums and decisive gates", "Heading1"),
             paragraph("Use the L corner as the cap A1 datum. Keep F.SilkS outward and B.Cu mating downward. Match the rectangular pad grid before rotating the complete carrier. Never rotate a cap 90 degrees relative to its site. The allocation puts one carrier at 0 degrees and one at 90 degrees in every confirmation run. Fixed carrier-site diagonal effects remain a limitation."),
             table([["Gate", "Required evidence"],
                    ["Fabrication", "CNC-route caps. No V-score. Finished copper-to-edge clearance >=0.2 mm. Target pad-diameter tolerance +/-5 um. Return final panel and CAM."],
                    ["Spheres", "At least 1,200 accepted spheres. Each measured diameter interval must lie wholly inside 317.5 to 322.5 um, with expanded U <=1 um."],
                    ["Free settling", "Measured bare-cap load. No cap spacer, clamp, adhesive, contacting probe or attached thermal lead during the liquid hold."],
                    ["Metrology", "All twenty pad faces for a whole-cap minimum. Expanded local gap U <=2 um and paired-difference U <=3 um at k=2. Registered sections check 3D metrology."],
                    ["Prospective order", "Qualify dwell on pilot. Place and measure actual confirmation offsets, then freeze inputs and predictions, then reflow, then measure held-out outcomes."],
                    ["Model boundary", "Explicit observed wetting and contact-line evidence. Do not infer eligibility from an absence of defects."],
                    ["Physical conclusion", "Cold geometry supports only the measured process comparison. Optional hot-state metrology is separately quoted and must demonstrate liquid state and uncertainty."]], [105, 399]),
             paragraph("Keep these reference planes separate", "Heading2"),
             paragraph("The study threshold is 185 um between opposing finished pad faces. It is not a mask-to-cap requirement. Return both pad-face gaps and actual mask-to-cap underbody clearance. Include copper, nickel and gold in finished metal height. Two-pad-cylinder geometry is a fixed secondary approximation, not solder inside copper."),
             paragraph("The native planning calculations bracket the threshold differently. Literal rims predict 223.32 / 207.52 um for C220 / C270; the two-pad approximation predicts 178.20 / 167.31 um. These are artificial planning inputs, not registered laboratory predictions. The experiment must resolve the geometry uncertainty."),
             PageBreak(), paragraph("Parts, services and quote scope", "Heading1")]
    with (HERE / "BOM.csv").open() as source:
        items = list(csv.DictReader(source))
    story.append(table([["Item", "Quantity", "Description / acceptance"]]+[
        [row["item"], row["quantity"]+" "+row["unit"], row["description"]+". "+row["procurement_status"].replace("_", " ")]
        for row in items], [72, 80, 352]))
    story.extend([paragraph("Read LAB_RFQ.md and PROCUREMENT.md for the full staged quote, source links, panel responsibility, return data, and material acceptance. Exact sphere supply, MOQ, price, schedule, and whole-cap metrology capability remain unconfirmed. Quote hot-state work and any additional specimens separately."),
                  paragraph("The following procedure is generated from PROCEDURE.md. Keep the controlled JSON, allocation CSV, native boards, Gerbers, BOM, and blank data worksheets with this guide. The PDF is an assembly and operating guide. Fabrication dimensions come from accepted CAD and CAM."), PageBreak()])
    markdown(story, HERE / "PROCEDURE.md")
    document = SimpleDocTemplate(str(output), pagesize=(612, 792), rightMargin=54, leftMargin=54,
                                 topMargin=42, bottomMargin=52, title="SolderShape outside-lab coupon handoff",
                                 author="SolderShape project")
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    main()
