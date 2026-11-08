# /// script
# requires-python = ">=3.11"
# dependencies = ["python-docx>=1.1"]
# ///
"""Generate the synthetic fixture brief.docx (invented content, no real data).

Run from this directory:  uv run make_brief.py
Then refresh the base64 payload in ../scaffold.sh:  base64 -i brief.docx
"""
from docx import Document

doc = Document()
doc.add_heading("ขอบเขตงานจ้างพัฒนาระบบจองห้องประชุม (ตัวอย่างสมมติ)", level=1)
doc.add_paragraph(
    "เอกสารฉบับนี้เป็นข้อมูลสมมติที่สร้างขึ้นเพื่อใช้ทดสอบเท่านั้น "
    "ไม่อ้างอิงหน่วยงาน บุคคล หรือโครงการจริงใด ๆ"
)
doc.add_heading("1. วัตถุประสงค์", level=2)
doc.add_paragraph("พัฒนาระบบจองห้องประชุมภายในสำหรับพนักงานประมาณ 120 คน ใช้งานผ่านเว็บเบราว์เซอร์")
doc.add_heading("2. ขอบเขตงาน", level=2)
for item in ["จองห้องประชุมล่วงหน้าได้ไม่เกิน 30 วัน", "ยกเลิกการจองได้ก่อนเวลาเริ่ม 2 ชั่วโมง", "ส่งอีเมลยืนยันการจองอัตโนมัติ"]:
    doc.add_paragraph(item, style="List Bullet")
doc.add_heading("3. งบประมาณโดยประมาณ", level=2)
table = doc.add_table(rows=1, cols=3)
table.style = "Table Grid"
hdr = table.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text = "รายการ", "จำนวน", "ราคา (บาท)"
for row in [("ออกแบบระบบ", "1 งาน", "45,000"), ("พัฒนาและทดสอบ", "1 งาน", "180,000"), ("อบรมผู้ใช้", "2 รอบ", "15,000")]:
    cells = table.add_row().cells
    for c, v in zip(cells, row):
        c.text = v
doc.add_paragraph("รวมทั้งสิ้น 240,000 บาท (ตัวเลขสมมติ)")
doc.save("brief.docx")
print("wrote brief.docx")
