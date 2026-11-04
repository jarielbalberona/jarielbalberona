from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, HRFlowable
from xml.sax.saxutils import escape
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public' / 'jariel-balberona-cv.pdf'
data = json.loads((ROOT / 'src' / 'data' / 'cv.json').read_text())
font_dir = Path('/System/Library/Fonts/Supplemental')
if (font_dir / 'Arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('CV', str(font_dir / 'Arial.ttf')))
    pdfmetrics.registerFont(TTFont('CV-Bold', str(font_dir / 'Arial Bold.ttf')))
else:
    from reportlab.pdfbase.pdfmetrics import Font
    pdfmetrics.registerFont(Font('CV', 'Helvetica', 'WinAnsiEncoding'))
    pdfmetrics.registerFont(Font('CV-Bold', 'Helvetica-Bold', 'WinAnsiEncoding'))
pdfmetrics.registerFontFamily('CV', normal='CV', bold='CV-Bold', italic='CV', boldItalic='CV-Bold')
navy=colors.HexColor('#17364D'); ink=colors.HexColor('#26333D'); muted=colors.HexColor('#596774'); blue=colors.HexColor('#245B80')
styles={
'name':ParagraphStyle('name',fontName='CV-Bold',fontSize=25,leading=29,textColor=navy,spaceAfter=6),
'headline':ParagraphStyle('headline',fontName='CV-Bold',fontSize=11.4,leading=15,textColor=ink,spaceAfter=7),
'meta':ParagraphStyle('meta',fontName='CV',fontSize=9.1,leading=13,textColor=muted,spaceAfter=3),
'body':ParagraphStyle('body',fontName='CV',fontSize=10,leading=14,textColor=ink,spaceAfter=5),
'bullet':ParagraphStyle('bullet',fontName='CV',fontSize=10,leading=13.6,textColor=ink,leftIndent=10,firstLineIndent=0,bulletIndent=0,spaceAfter=5),
'section':ParagraphStyle('section',fontName='CV-Bold',fontSize=10.2,leading=13,textColor=navy,spaceBefore=13,spaceAfter=6,keepWithNext=True),
'job':ParagraphStyle('job',fontName='CV-Bold',fontSize=10.6,leading=14,textColor=navy,spaceAfter=3,keepWithNext=True),
'skill':ParagraphStyle('skill',fontName='CV',fontSize=9.5,leading=13.2,textColor=ink,spaceAfter=3),
'earlier':ParagraphStyle('earlier',fontName='CV',fontSize=9.4,leading=13.2,textColor=ink,spaceAfter=5),
}
story=[]
def p(t,k='body'):return Paragraph(t,styles[k])
def section(t):story.append(p(t.upper(),'section'));story.append(HRFlowable(width='100%',thickness=.45,color=colors.HexColor('#CBD6DF'),spaceAfter=6))
def bullet(t):return Paragraph(escape(t),styles['bullet'],bulletText='\u2022')
def job(company,title,meta,bullets,summary=None,url=None):
 c=f'<link href="{url}" color="#17364D">{escape(company)}</link>' if url else escape(company)
 items=[p(c+' | '+escape(title),'job'),p(escape(meta),'meta')]
 if summary:items.append(p(escape(summary)))
 items += [bullet(b) for b in bullets]
 items.append(Spacer(1,7))
 story.append(KeepTogether(items))

story += [p(escape(data['name']), 'name'), p(escape(data['headline']), 'headline'),
          p(escape(data['location']), 'meta'),
          p(f'<link href="mailto:{data["email"]}" color="#245B80">{escape(data["email"])}</link>  |  {escape(data["phone"])}', 'meta'),
          p(f'<link href="https://{data["website"]}" color="#245B80">{escape(data["website"])}</link>  |  <link href="https://{data["github"]}" color="#245B80">{escape(data["github"])}</link>  |  <link href="https://{data["linkedin"]}" color="#245B80">LinkedIn</link>', 'meta')]
section('Profile')
story.append(p(escape(data['summary'])))
section('Core capabilities')
for capability in data['skillGroups']:
    story.append(p(capability, 'skill'))
for current, heading in [(True, 'Current experience'), (False, 'Previous experience')]:
    if not current:
        story.append(PageBreak())
    section(heading)
    for entry in data['experience']:
        if entry['current'] == current:
            job(entry['company'], entry['role'], entry['meta'], entry['highlights'], url=entry.get('url'))
section('Earlier experience')
for entry in data['earlierExperience']:
    story.append(p(entry, 'earlier'))
section('Education')
for degree in data['education']:
    story.append(p(f'<b>{escape(degree)}</b>'))
section('Selected technical writing')
for writing in data['writing']:
    story.append(p(f'<link href="{writing["url"]}" color="#245B80"><b>{escape(writing["title"])}</b></link> - {escape(writing["description"])}', 'earlier'))

def footer(canvas,doc):
 canvas.saveState(); w,h=A4
 if doc.page>1:
  canvas.setFillColor(muted);canvas.setFont('CV',8.4);canvas.drawString(46,h-30,'JARIEL BALBERONA | SOFTWARE ENGINEERING')
 canvas.setStrokeColor(colors.HexColor('#D8E0E6'));canvas.setLineWidth(.45);canvas.line(46,37,w-46,37)
 canvas.setFont('CV',8);canvas.setFillColor(muted);canvas.drawString(46,24,'Jariel Balberona');canvas.drawRightString(w-46,24,f'{doc.page}')
 canvas.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=46,rightMargin=46,topMargin=41,bottomMargin=49,title='Jariel Balberona - Software Engineering CV',author='Jariel Balberona',subject='Senior Software Engineer | AI Product & Platform Engineering')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(f'Generated {OUT}')
