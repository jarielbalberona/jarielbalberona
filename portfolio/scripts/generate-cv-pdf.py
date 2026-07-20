#!/usr/bin/env python3

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "data" / "cv.json"
OUTPUT = ROOT / "public" / "jariel-balberona-cv.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Name",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=24,
            spaceAfter=6,
            textColor=colors.HexColor("#111111"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Headline",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            spaceAfter=8,
            textColor=colors.HexColor("#444444"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#555555"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaRight",
            parent=styles["Meta"],
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor("#111111"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#222222"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["Body"],
            fontSize=8,
            leading=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletItem",
            parent=styles["Body"],
            leftIndent=10,
            firstLineIndent=0,
            bulletIndent=0,
            spaceAfter=2,
        )
    )
    return styles


def line(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bullet(text, styles):
    return Paragraph(f"&bull; {line(text)}", styles["BulletItem"])


def section_header(text, styles):
    return Paragraph(line(text.upper()), styles["Section"])


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.5 * inch, str(doc.page))
    canvas.restoreState()


def entry_block(entry, styles):
    header = Paragraph(
        f"<b>{line(entry['company'])}</b> | {line(entry['role'])} | {line(entry.get('employmentType', ''))}",
        styles["Body"],
    )
    meta = Paragraph(
        f"{line(entry['dateRange'])} | {line(entry['location'])}",
        styles["Meta"],
    )
    summary = Paragraph(line(entry["summary"]), styles["Body"])
    tech = Paragraph(f"<b>Tech:</b> {line(', '.join(entry['tech']))}", styles["Small"])
    items = [header, meta, Spacer(1, 4), summary, Spacer(1, 4), tech, Spacer(1, 4)]
    items.extend(bullet(item, styles) for item in entry["highlights"])
    return KeepTogether(items + [Spacer(1, 8)])


def work_block(entry, styles):
    header = Paragraph(f"<b>{line(entry['name'])}</b> | {line(entry['label'])}", styles["Body"])
    summary = Paragraph(line(entry["summary"]), styles["Body"])
    tech = Paragraph(f"<b>Tech:</b> {line(', '.join(entry['tech']))}", styles["Small"])
    items = [header, Spacer(1, 2), summary, Spacer(1, 4), tech, Spacer(1, 4)]
    items.extend(bullet(item, styles) for item in entry["highlights"])
    return KeepTogether(items + [Spacer(1, 8)])


def earlier_block(entry, styles):
    return Paragraph(
        f"<b>{line(entry['company'])}</b> | {line(entry['role'])} | {line(entry['employmentType'])}<br/>"
        f"{line(entry['dateRange'])} | {line(entry['location'])}<br/>{line(entry['details'])}",
        styles["Body"],
    )


def main():
    data = json.loads(SOURCE.read_text())
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.7 * inch,
        title=f"{data['name']} CV",
        author=data["name"],
    )

    story = [
        Paragraph(line(data["name"]), styles["Name"]),
        Paragraph(line(data["headline"]), styles["Headline"]),
        Paragraph(
            " | ".join(
                [
                    line(data["location"]),
                    line(data["email"]),
                    line(data["phone"]),
                    line(data["website"]),
                    line(data["github"]),
                    line(data["linkedin"]),
                ]
            ),
            styles["Meta"],
        ),
        Spacer(1, 10),
        section_header("Summary", styles),
        Paragraph(line(data["summary"]), styles["Body"]),
        section_header("Core Skills", styles),
    ]

    for group in data["skillGroups"]:
        story.append(
            Paragraph(
                f"<b>{line(group['title'])}:</b> {line(', '.join(group['items']))}",
                styles["Body"],
            )
        )
        story.append(Spacer(1, 2))

    story.append(section_header("Experience", styles))
    for entry in data["experience"]:
        story.append(entry_block(entry, styles))

    story.append(section_header("Selected Work", styles))
    for entry in data["selectedWork"]:
        story.append(work_block(entry, styles))

    story.append(section_header("Earlier Experience", styles))
    for entry in data["earlierExperience"]:
        story.append(earlier_block(entry, styles))
        story.append(Spacer(1, 6))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


if __name__ == "__main__":
    main()
