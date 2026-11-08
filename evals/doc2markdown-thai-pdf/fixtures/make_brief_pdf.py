# /// script
# requires-python = ">=3.11"
# dependencies = ["reportlab>=4.0"]
# ///
"""Generate brief.pdf — a synthetic Thai PDF whose text layer carries the
SARA AM defect doc2markdown's pdf_text.py repairs: every ำ is written as the
decomposed pair NIKHAHIT (U+0E4D) + SARA AA (U+0E32), exactly what many Thai
fonts leave in the text layer. Naive extraction yields "ทํา"; the repaired
layer yields "ทำ". Invented content only.

Run from this directory on macOS:  uv run make_brief_pdf.py
Then refresh the base64 payload in ../scaffold.sh:  base64 -i brief.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

FONT = "/System/Library/Fonts/Supplemental/Ayuthaya.ttf"
pdfmetrics.registerFont(TTFont("ThaiFx", FONT))

NIKHAHIT, SARA_AA, SARA_AM = "ํ", "า", "ำ"


def damage(text: str) -> str:
    """Write every ำ as the decomposed glyph pair."""
    return text.replace(SARA_AM, NIKHAHIT + SARA_AA)


title = "บันทึกข้อความ เรื่อง แนวทางการจัดการพื้นที่ส่วนกลางของอาคารสำนักงาน (ตัวอย่างสมมติ)"
paras = [
    "เอกสารฉบับนี้เป็นข้อมูลสมมติที่สร้างขึ้นเพื่อทดสอบการแปลงเอกสารเท่านั้น ไม่อ้างอิงหน่วยงาน บุคคล หรือสถานที่จริงแต่อย่างใด",
    "ตามที่อาคารได้เปิดใช้พื้นที่ส่วนกลางชั้นสามเป็นห้องอ่านหนังสือและพื้นที่พักผ่อนมาตั้งแต่ต้นปี ปรากฏว่ามีผู้ใช้งานจำนวนมากในช่วงเวลาพักกลางวัน ทางฝ่ายอาคารจึงขอกำหนดแนวทางการใช้งานเพื่อให้ทุกคนได้ใช้พื้นที่อย่างสะดวกและเป็นธรรม",
    "ข้อหนึ่ง ขอให้ผู้ใช้งานทำความสะอาดโต๊ะและเก้าอี้หลังใช้งานทุกครั้ง และนำภาชนะอาหารไปทิ้งในจุดที่จัดไว้ ข้อสอง การจองพื้นที่สำหรับกิจกรรมกลุ่มให้แจ้งล่วงหน้าอย่างน้อยสามวันทำการผ่านแบบฟอร์มของฝ่ายอาคาร ข้อสาม ห้ามนำอุปกรณ์เสียงดังเข้ามาใช้ในพื้นที่ เว้นแต่ได้รับอนุญาตเป็นลายลักษณ์อักษร",
    "ฝ่ายอาคารจะประเมินผลการใช้งานทุกไตรมาส และอาจปรับเปลี่ยนแนวทางตามความเหมาะสม หากมีข้อเสนอแนะสามารถแจ้งได้ที่เคาน์เตอร์ประชาสัมพันธ์ชั้นหนึ่งในวันและเวลาราชการ",
]
styles = {
    "h": ParagraphStyle("h", fontName="ThaiFx", fontSize=16, leading=24, spaceAfter=12),
    "p": ParagraphStyle("p", fontName="ThaiFx", fontSize=12, leading=20, spaceAfter=8),
}
doc = SimpleDocTemplate("brief.pdf", pagesize=A4, title="brief (fixture)")
story = [Paragraph(damage(title), styles["h"])]
for p in paras:
    story.append(Paragraph(damage(p), styles["p"]))
    story.append(Spacer(1, 4))
doc.build(story)
print("wrote brief.pdf")
