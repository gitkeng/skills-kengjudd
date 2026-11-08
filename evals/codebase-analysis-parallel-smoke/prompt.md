---
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit, Agent, TodoWrite]
---

วิเคราะห์โค้ดเบสในโฟลเดอร์นี้แบบละเอียดด้วย codebase-analysis โดยใช้โหมดรัน phase คู่ขนาน (parallel mode) เขียนผลลัพธ์ไว้ที่ ./codebase-analysis ให้ครบทุกไฟล์ตามที่ skill กำหนด และรัน validator ให้ผ่านก่อนจบ
