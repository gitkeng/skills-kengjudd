# ผลการ review คุณภาพ skill ทั้ง 7 ตัว และข้อเสนอการปรับปรุง (2026-11-08)

เอกสารนี้เป็น**ข้อเสนอเพื่อให้ผู้ดูแลตัดสินใจ** ยังไม่มีการเปลี่ยนแปลงใด ๆ ใน `skills/`,
`knowledge/` หรือไฟล์เวอร์ชัน ณ วันที่ออกเอกสาร การตรวจสอบทำบน working tree
ปัจจุบัน (repo `0.14.0`, มีงาน init-project 1.2.0 ที่ยัง uncommitted อยู่)
ข้อเสนอทุกข้อจึงควรลงมือ**หลัง** commit งานชุดนั้นก่อน

หมายเหตุด้านภาษา: ชื่อไฟล์ key ใน YAML ชื่อ flag และศัพท์เทคนิคคงไว้เป็นภาษาอังกฤษ

---

## 1. บทสรุปผู้บริหาร

**ภาพรวม:** skill ทั้ง 7 ตัวผ่าน spec agentskills.io ครบ (ใช้เฉพาะ 6 field,
`name` ตรงกับ directory, มี `## Updating`, มี validator script ใน 4 ตัว)
และใช้ progressive disclosure ได้ดีกว่าค่าเฉลี่ยของ ecosystem โครงสร้างพื้นฐาน
(install.sh, update.sh, bump-version.sh, OKF knowledge base) ยังถูกต้องและ
ตรงกับ discovery path ปัจจุบันของทุก agent ที่ตรวจสอบได้

**สิ่งที่ล้าสมัยที่สุดไม่ใช่ตัว skill แต่เป็น "วิธีทดสอบและวัดผล"** skill ทุกตัว
ถูกแตะครั้งสุดท้ายช่วง 30–31 ส.ค. 2026 (init-project 7 ก.ย.) ขณะที่ Claude Code
เพิ่ม `/skill-doctor` (2.1.261), `claude plugin eval` (2.1.269) และกฎ
re-attach หลัง compaction ที่จำกัด 5,000 token ต่อ skill เข้ามาหลังจากนั้น
รีโปยังไม่มีชุด eval แม้แต่ชุดเดียว และ checklist ยังสั่งให้ทดสอบ trigger
ด้วยมือใน session ใหม่

**ต้นทุน token ที่แก้ได้ทันทีโดยไม่แตะ skill:** ในโปรเจกต์นี้ skill ทุกตัวถูกโหลด
**สองช่องทางพร้อมกัน** (symlink ใน `.claude/skills/` และ plugin `kengjudd@kengjudd`
0.13.0 ใน user scope) ทำให้ description ประมาณ 890 token ถูกจ่ายเป็น ~1,800 token
ทุกเทิร์น และ skill ชื่อเดียวกันสองตัวแข่งกัน trigger

**5 ข้อที่ให้ผลคุ้มค่าที่สุด** (รายละเอียดในส่วน 4–6)

| # | ข้อเสนอ | ผลที่ได้ | แรง |
|---|---|---|---|
| A | เลิกโหลดซ้ำสองช่องทางในโปรเจกต์นี้ | −~900 token/เทิร์น, ไม่มี skill ซ้ำแข่งกัน | ต่ำมาก |
| B | เพิ่ม `evals/` ต่อ skill ให้ `claude plugin eval` รันได้ เริ่มจาก git-commit และ doc2markdown | วัด trigger rate และ pass rate ได้จริง แทนการทดสอบด้วยมือ | กลาง |
| C | ย่อ `## Updating` จาก ~27 บรรทัดเหลือ ~8 และตัด boilerplate `readlink -f` ที่ซ้ำ | −~150–200 token ต่อการ activate × 7 skill | ต่ำ |
| D | แยก doc2markdown ออกเป็น SKILL.md สั้น + `references/{pdf,docx-xlsx,pptx}.md` โหลดตามชนิดไฟล์ | body จาก ~4,300 เหลือ ~2,000 token ต่อการรัน | กลาง |
| E | ปรับ description ทุกตัวให้ trigger word อยู่ใน 240 ตัวอักษรแรก และย่อ init-project (915 chars) | trigger ได้บน ZCode/Kimi ที่ตัด description ที่ 240–250 ตัวอักษร | ต่ำ |

---

## 2. วิธี review และแหล่งอ้างอิง

1. อ่าน SKILL.md ทั้ง 7 ตัว, template, authoring checklist และ KB ของรีโปเอง
2. วัดเชิงกล: จำนวนบรรทัด/ไบต์/token (ประมาณ ASCII÷4, ไทย÷1.5), ความยาว description,
   link integrity, orphan reference, TOC ใน reference >100 บรรทัด, `claude plugin validate .`
3. ค้นคว้าแหล่งทางการ ณ 2026-11-08 ผ่าน subagent สองตัว (ทุกข้ออ้างมี URL ในส่วน 10)
   — ข้อใดยืนยันบนหน้าเว็บไม่ได้ จะระบุว่า *unverified*

ข้อจำกัด: ยังไม่ได้รัน `/skill-doctor` หรือ `claude plugin eval` จริง (ไม่มี eval suite)
ตัวเลข token ในเอกสารนี้เป็นค่าประมาณ ไม่ใช่ค่าจาก tokenizer

---

## 3. ภาพรวมเชิงตัวเลข

| Skill | ver | แก้ล่าสุด | SKILL.md บรรทัด | body ≈token | description chars (≈token) | ไฟล์ทั้งหมด | .md รวม |
|---|---|---|---|---|---|---|---|
| init-project | 1.2.0 | 2026-09-07 | 439 | **6,350** | **915** (244) | 17 | 207 KB |
| doc2markdown | 1.1.1 | 2026-08-30 | 324 | 4,320 | 456 (136) | 11 | 17 KB |
| business-rules-extraction | 1.1.0 | 2026-08-31 | 188 | 3,860 | 419 (104) | 27 | 178 KB |
| creating-skills | 1.2.0 | 2026-08-30 | 214 | 2,840 | 309 (77) | 2 | 16 KB |
| codebase-analysis | 2.0.0 | 2026-08-31 | 223 | 2,810 | 393 (98) | 38 | 64 KB |
| git-commit | 1.0.1 | 2026-08-30 | 274 | 2,710 | 611 (161) | 1 | 11 KB |
| codebase-analysis-report | 1.1.0 | 2026-08-30 | 151 | 1,850 | 282 (70) | 14 | 30 KB |

เกณฑ์เทียบ

- spec แนะนำ body < 5,000 token และ < 500 บรรทัด → **init-project เกินเกณฑ์ token**
  แม้บรรทัดยังไม่เกิน
- งานวิจัย arXiv 2602.08004 (ก.พ. 2026, 40,285 skill) พบ median SKILL.md = 1,414 token,
  95th percentile = 5,077 → skill ของเราทุกตัวใหญ่กว่า median (คาดได้ เพราะเป็น
  orchestrator skill) แต่ init-project อยู่เหนือ 95th percentile
- Claude Code re-attach skill หลัง compaction เพียง **5,000 token แรกต่อ skill**
  (รวมกันไม่เกิน 25,000) → ส่วนท้ายของ init-project (Phase 5–6, Edge cases,
  ตาราง References) **หายไปหลัง compaction** ทุกครั้ง นี่คือความเสี่ยงเชิงพฤติกรรม
  ไม่ใช่แค่ต้นทุน

ผล `claude plugin validate .` (Claude Code 2.1.319): ผ่านพร้อมคำเตือน —
`LICENSE_MISSING` (plugin.json ไม่มี `license` และ root ไม่มีไฟล์ LICENSE)
ซึ่ง plugin directory ปฏิเสธการ submit, `ICON_MISSING`, และ `.DS_Store` ใน
working tree (ไม่ได้ track, อยู่ใน .gitignore แล้ว จึงไม่กระทบ)

---

## 4. ข้อค้นพบระดับรีโป (cross-cutting)

### 4.1 โหลดซ้ำสองช่องทาง — P0, แรงต่ำมาก

`.claude/skills/` ของโปรเจกต์นี้ symlink ไปทั้ง 7 skill (ตามที่ CLAUDE.md แนะนำ
เพื่อให้ทดสอบ trigger ได้) และ plugin `kengjudd@kengjudd` เวอร์ชัน 0.13.0 ก็ติดตั้งใน
user scope อยู่ด้วย ใน session นี้จึงเห็นทั้ง `creating-skills` และ
`kengjudd:creating-skills` เป็นต้น

ผลกระทบ: (ก) จ่าย token description สองเท่า (~1,800 token/เทิร์น), (ข) listing
budget ของ Claude Code คือ 1% ของ context window และเมื่อเกินจะ drop description
ของ skill ที่ถูกเรียกน้อยที่สุดก่อน — skill ซ้ำกินงบนี้ไปครึ่งหนึ่ง, (ค) เวอร์ชัน
ต่างกัน (plugin 0.13.0 vs ทรี 0.14.0) ทำให้ผลทดสอบ trigger ไม่น่าเชื่อถือ

ข้อเสนอ: เลือกหนึ่งช่องทางต่อเครื่อง เมื่อทำงานในรีโปนี้ให้ใช้ symlink และปิด plugin
ด้วย `skillOverrides` หรือ `claude plugin disable`; เพิ่มคำเตือนเรื่องนี้ใน
CLAUDE.md ส่วน "Working with skills" และใน `install.sh` (ตรวจ
`~/.claude/plugins/installed_plugins.json` แล้วเตือนถ้าพบ `kengjudd@kengjudd`)

### 4.2 ไม่มี eval suite และ checklist ยังทดสอบด้วยมือ — P0, แรงกลาง

`claude plugin eval` (ต้องการ 2.1.269+) รัน case จาก `<plugin>/evals/<case>/prompt.md`
+ grader (`regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`)
3 รอบต่อ arm, มี arm "ไม่มี plugin" เป็น baseline อัตโนมัติ, grader `tool_used: Skill`
วัด **trigger rate** ของ description โดยตรง, ออก `report.html` และ
`aggregate-result.json` — ตรงกับสิ่งที่ authoring checklist สั่งให้ทำด้วยมือ
("paste each prompt into a fresh session") ทุกประการ

ข้อเสนอ:

1. สร้าง `evals/` ที่ root ของ plugin (ที่เดียวกับ `.claude-plugin/`) หนึ่ง case
   directory ต่อ skill ต่อสถานการณ์ เริ่มจาก skill ที่ผลลัพธ์ตรวจได้เชิงกล:
   - `git-commit`: prompt ไทย "คอมมิตให้หน่อย" บน fixture repo → grader
     `tool_used: Skill`, `regex` บน output ว่ามี emoji+type, `tool_used: Bash`
     ที่ `input_match` ต้องไม่มี `git add -A`
   - `doc2markdown`: prompt ไทยกับไฟล์ .docx ตัวอย่าง → `file_exists` ของ `.md`
     และ `assets/`, `regex` ว่าไม่มี `[unreadable]` เกินเกณฑ์
   - anti-trigger case: prompt ใกล้เคียง (เช่น "git push" หรือ "สรุปเอกสารนี้ให้")
     ที่ `tool_used: Skill` ต้อง**ไม่**เกิด
2. แก้ `authoring-checklist.md` ส่วน "Testing before calling it done": ช่องทาง Claude
   Code ใช้ `claude plugin eval . --case <skill>*`; การทดสอบด้วยมือเหลือไว้สำหรับ
   agent อื่น
3. บันทึกรูปแบบ eval เป็น `knowledge/decisions/<date>-eval-suite-layout.md`
   (KB `best-practices.md` §6 ระบุชัดว่าถ้าจะมี eval ต้องตกลง layout และบันทึกเป็น
   decision ก่อน)

ทางเลือกเสริม: skill-creator plugin ที่ติดตั้งอยู่มี `scripts/run_loop.py` สำหรับ
optimize description (20 query, split 60/40, ≤5 รอบ) ใช้ได้กับ skill ที่
under-trigger โดยไม่ต้องเขียน grader เอง แต่ต้องการ `claude -p` และใช้เวลานาน

### 4.3 `## Updating` และ boilerplate ซ้ำกินงบทุกครั้งที่ activate — P1, แรงต่ำ

ส่วน `## Updating` ยาว 24–30 บรรทัด (~836 ไบต์ ≈ 210 token) เหมือนกันทั้ง 7 skill
และ 6 ใน 7 ตัวยังมีย่อหน้า `readlink -f` ซ้ำทั้งใน body และใน Updating
CLAUDE.md กฎข้อ 3 ต้องการเพียง "ครอบคลุมทั้งสองช่องทาง" ไม่ได้กำหนดความยาว

ข้อเสนอ (แก้ใน template แล้วไล่ทุก skill):

```markdown
## Updating

Versioned by `metadata.version`; source: private repo `gitkeng/skills-kengjudd`.

- Git-clone/symlink install (repo root; resolve a symlinked skill dir with `readlink -f`):
  `./scripts/update.sh <skill-name>`
- Claude Code plugin install (no `.git` in the plugin cache, so `update.sh` cannot run):
  `claude plugin update kengjudd@kengjudd`

Then reload skills (Claude Code hot-reloads edited SKILL.md; new directories need `/reload-skills`) or restart the session.
```

ประหยัด ~150 token ต่อการ activate และอัปเดตข้อเท็จจริงเรื่อง hot reload ด้วย
(ปัจจุบันเขียนว่าต้อง restart เสมอ ซึ่งไม่จริงสำหรับ Claude Code แล้ว)

### 4.4 Description: ความยาวและลำดับคำ trigger — P1, แรงต่ำ

ข้อเท็จจริงใหม่ที่กระทบ:

- Claude Code ตัด `description` (+`when_to_use`) ที่ **1,536 ตัวอักษร** และแนะนำให้
  "key use case first"
- **ZCode** แสดง description เพียง **250 ตัวอักษรแรก** ต่อเทิร์น และ **drop skill ทิ้ง**
  ถ้าเกิน 1,024; **Kimi** ตัด fallback ที่ **240**; **Codex** "ย่อ description ก่อน"
  เมื่องบ context เต็ม
- ตัวอักษรไทยกิน token ราว 1 ต่อ 1.5 ตัวอักษร (สูงกว่าอังกฤษ ~2.7 เท่า)

ตรวจ 240 ตัวอักษรแรกของแต่ละ description:

| Skill | 240 ตัวอักษรแรกมี trigger word? | ปัญหา |
|---|---|---|
| business-rules-extraction | ไม่ — "Triggers on: …" อยู่หลังตัวอักษรที่ ~300 | ย้ายวลี trigger ขึ้นหน้า |
| codebase-analysis | บางส่วน — "Use for …" เริ่มที่ ~250 | ย้าย "Use for codebase analysis, architecture docs…" ขึ้นประโยคที่สอง |
| codebase-analysis-report | ใช่ | — |
| creating-skills | ใช่ | — |
| doc2markdown | ใช่ (แต่วลีไทยอยู่ท้าย) | ย้ายวลีไทย 1–2 วลีขึ้นมาในช่วงแรก |
| git-commit | ใช่ (611 chars, วลีไทยอยู่กลาง) | ย่อประโยคอธิบายกลไก |
| init-project | ใช่ แต่ยาว 915 chars | ตัด "Not for …" ที่ยาวออกไปไว้ใน body หรือย่อให้เหลือ ≤ 600 |

หลักการเขียนใหม่ที่เสนอให้ใส่ใน checklist: *ประโยคแรก = ทำอะไร + ใช้เมื่อไร
พร้อมคำที่ผู้ใช้พิมพ์จริง (รวมไทย) ให้จบใน 240 ตัวอักษร; ประโยคถัดไปขยาย; "Not for"
สั้น ๆ ท้ายสุด; เป้าหมายความยาวรวม 300–600 ตัวอักษร*

### 4.5 Reference file >100 บรรทัดที่ไม่มี TOC — P2

checklist ของรีโปเองกำหนดให้มี TOC แต่พบ 14 ไฟล์ที่ไม่มี:
`codebase-analysis-report/references/validation.md` (115),
`business-rules-extraction/references/{pitfalls (154), taxonomy (129), rule-schema (299)}.md`
และ playbooks `go, dart-flutter, scale, apple, rust, mainframe, beam, native,
typescript-react-next, automation` (106–191 บรรทัด)
แนวทาง Anthropic ระบุว่า agent อาจ `head -100` ไฟล์ที่ลึก ดังนั้น TOC ช่วยให้
อ่านเฉพาะ section ได้จริง

### 4.6 Plugin manifest — P2, แรงต่ำมาก

- เพิ่ม `"license": "MIT"` ใน `.claude-plugin/plugin.json` (skill 2 ตัวประกาศ MIT อยู่แล้ว;
  ให้ยืนยันว่าทั้งรีโปตั้งใจใช้ MIT ก่อน) หรือวาง `LICENSE` ที่ root
- icon เป็นทางเลือก ไม่จำเป็นสำหรับ private marketplace
- `.gitignore` มี `.DS_Store` แล้ว แต่ไฟล์ยังอยู่ใน working tree — ลบออกจากเครื่อง

### 4.7 `allowed-tools` ของ git-commit ไม่ตรงรูปแบบ spec — P2

spec กำหนดเป็น **space-separated string** (`Bash(git status:*) Bash(git diff:*) …`)
แต่ git-commit เขียนเป็น YAML list `skills-ref validate` ไม่ type-check field นี้
จึงผ่าน แต่ agent ที่ parse ตาม spec อาจละเลยทั้ง field ให้แปลงเป็น string หนึ่งบรรทัด

### 4.8 KB ล้าสมัยบางจุด — P2

- `knowledge/skill-authoring/best-practices.md` §6 และ §8 เขียนตอนยังไม่มี eval
  tooling ในตัว → เพิ่ม `claude plugin eval`, `/skill-doctor`, กฎ 5,000-token
  หลัง compaction, งบ listing 1%/1,536 chars และข้อจำกัดของ ZCode/Kimi/Codex
- `knowledge/specs/agent-skills-spec.md` ระบุ "25+ agents" → ปัจจุบัน client
  showcase 46 ราย และ spec ถูกบริจาคให้ Agentic AI Foundation (Linux Foundation)
  เมื่อ 2026-10-22 พร้อม roadmap "versioned releases" (ยังไม่มี release จริง)
  → `check-spec-versions.sh` ตรวจเฉพาะ OKF ควรเพิ่มการตรวจ commit hash ของ
  `docs/specification.mdx` ใน `agentskills/agentskills` เพื่อให้กฎข้อ 5 ครอบคลุม
  spec ที่สองด้วย
- `knowledge/agents/skill-discovery-matrix.md` (2026-08-29) ควร re-verify:
  Gemini CLI ถูกแทนด้วย Antigravity CLI สำหรับ tier ฟรีตั้งแต่ 2026-06-18
  (banner บนหน้า docs), เอกสาร Codex ย้ายไป `learn.chatgpt.com` (308), Kimi CLI
  เดิมถูก archive → Kimi Code CLI, Claude Code **ยังไม่อ่าน** `.agents/skills/`
  (issue #31005 เปิดอยู่) — install.sh ปัจจุบัน map ถูกต้องทุกตัว ไม่ต้องแก้ script
- URL `docs.claude.com` redirect ไป `platform.claude.com` — KB ใช้ platform อยู่แล้ว ✓

---

## 5. ข้อค้นพบราย skill

### 5.1 init-project (1.2.0) — ใหญ่เกิน 5,000 token และเสี่ยงหลัง compaction

จุดแข็ง: progressive disclosure ดีมาก (สั่ง "read only the `## <agent>` section",
extract ≤ 8 บรรทัดต่อ agent, reference 9 ไฟล์มี TOC) iron rules ชัด มี validator
พร้อม `--self` gate

ประเด็น:

1. **body ≈ 6,350 token > 5,000** และข้อความหลัง token ที่ 5,000 (ราว Phase 5 ลงไป)
   จะไม่ถูก re-attach หลัง compaction — การรัน init-project ที่ยาวหลายสิบเทิร์นมี
   โอกาส compaction สูง จึงกระทบจริง
2. Phase 1 ข้อ 5–6 (ชื่อโฟลเดอร์ KB, legacy folders) และ Phase 4 ข้อ 2 (Canonical
   file) เป็น "วิธีทำ" ละเอียดที่ซ้ำกับ reference ที่ลิงก์อยู่แล้ว
3. description 915 ตัวอักษร — ยาวที่สุดในรีโป เกิน 2 เท่าของค่าที่ Codex/ZCode
   ยังแสดงครบ

ข้อเสนอ (minor bump → 1.3.0): ย้าย Phase 1 ข้อ 5–9 และ Phase 4 ข้อ 2–5 ไปเป็น
`references/phase-interview.md` และ `references/phase-context-files.md` ตามลำดับ
โดยคง 1 บรรทัดสรุป + ลิงก์ใน SKILL.md; เป้าหมาย body ≤ 4,000 token เพื่อให้ทั้ง
ไฟล์อยู่ในงบ re-attach; ย่อ description เหลือ ≤ 600 โดยคงวลีไทย 3 วลีแรกไว้

### 5.2 doc2markdown (1.1.1) — ตัวอย่างที่ดีของ scripts-first แต่ body โหลดทุกชนิดไฟล์พร้อมกัน

จุดแข็ง: scripts ทำงาน deterministic ด้วย `uv run` + PEP 723 (ไม่ต้องติดตั้งอะไร),
subagent fan-out สำหรับ OCR, `merge.py --strict` เป็น validator loop,
ส่วน "Why the scripts exist" อธิบายเหตุผลแทน MUST — ตรงแนวทาง Anthropic ทั้งหมด

ประเด็น: การรันกับ PDF หนึ่งไฟล์ต้องโหลด flag ของ pptx 10 ข้อ, brief ของ pptx
และตาราง part-naming ของ docx/xlsx ทั้งหมด (~2,000 token ที่ไม่เกี่ยว)

ข้อเสนอ (minor → 1.2.0): เหลือใน SKILL.md เฉพาะ Requirements, Layout, Step 1–4
แบบย่อ, Fidelity rules (ใช้ร่วมทุกชนิด) และ Why the scripts exist; ย้ายรายการ
manifest flags + brief + part naming ของแต่ละชนิดไป `references/pdf.md`,
`references/docx-xlsx.md`, `references/pptx.md` แล้วสั่ง "อ่านไฟล์ของชนิดที่
`probe.py` รายงานเท่านั้น" — รูปแบบ "organise by variant" ที่ Anthropic แนะนำ
ลบ `scripts/__pycache__/` ออกจากเครื่อง (ไม่ได้ track แต่จะติดไปกับ plugin cache
ถ้า copy ทั้ง tree)

### 5.3 git-commit (1.0.1) — สมบูรณ์ แก้เฉพาะรูปแบบ

จุดแข็ง: guard ครบ (merge state, detached HEAD, no commits yet, pre-staged leakage,
hook failure), `allowed-tools` จำกัดขอบเขต, ตัวอย่างชัด

ข้อเสนอ (patch → 1.0.2): แปลง `allowed-tools` เป็น string ตาม spec (4.7);
ย่อ description ให้ส่วนอธิบายกลไก ("by analyzing the whole working tree — staged,
unstaged, and untracked changes — group…") สั้นลง เหลือพื้นที่ให้วลีไทยอยู่ใน
240 ตัวอักษรแรก; เป็น candidate แรกของ eval suite (ผลตรวจได้เชิงกลทั้งหมด)

หมายเหตุ: Claude Code 2.1.286 กำหนดว่า skill ชื่อ `verify` จะถูกรันก่อน commit
อัตโนมัติ — ไม่กระทบ git-commit แต่ควรบันทึกใน CLAUDE.md "Skill naming" ว่าชื่อ
`verify` เป็นชื่อสงวนเชิงพฤติกรรม

### 5.4 creating-skills (1.2.0) — ส่วน Skill prefixes กินพื้นที่สำหรับการตัดสินใจที่จบไปแล้ว

ส่วน `## Skill prefixes` ~50 บรรทัด (~700 token) อธิบาย flow "ถามผู้ใช้เมื่อรีโป
ไม่มี plugin" ซึ่งไม่เกิดในรีโปนี้อีกแล้ว (plugin `kengjudd` มีแล้ว) และเนื้อหาเดียวกัน
อยู่ใน `knowledge/skill-authoring/skill-prefixes.md` แล้ว

ข้อเสนอ (minor → 1.3.0):

- ย่อ Skill prefixes เหลือ 5 บรรทัด + ลิงก์ไป `references/skill-prefixes.md`
  (ย้ายข้อความเต็มมาไว้ใน references เพราะ KB อยู่นอก skill และไม่ติดไปกับ symlink)
- เพิ่มขั้นตอนใหม่ในทั้งสอง workflow: "เขียน/อัปเดต eval case ใน `evals/`" และ
  "รัน `claude plugin eval` ก่อน bump" (หลังตัดสินใจ 4.2)
- เพิ่มกฎ description ใหม่ (4.4) และกฎ "5,000 token แรกต้องครบงาน" ใน checklist
- อัปเดต template ตาม 4.3

### 5.5 codebase-analysis (2.0.0) — ดีอยู่แล้ว ปรับเล็ก

จุดแข็ง: "Load only …" ต่อ phase ชัดเจนที่สุดในรีโป, checkpoint ทุก phase,
canonical-key/alias สำหรับ re-run, validator

ประเด็น: `references/language-*.md` 8 ไฟล์ถูกอ้างด้วย glob ผ่าน `languages.md`
(สองชั้น) — ยอมรับได้เพราะ router เป็นไฟล์เดียวที่สั่งให้โหลด แต่ควรระบุรายชื่อ
8 ไฟล์ในตารางท้าย SKILL.md เพื่อให้ one-level-deep ตามตัวอักษร; Phase 2–7
รันต่อเนื่องใน context เดียว ทั้งที่แต่ละ phase โหลด reference คนละชุดและเขียน
ไฟล์คนละโฟลเดอร์

ข้อเสนอ (patch → 2.0.1 สำหรับตาราง; minor → 2.1.0 ถ้าทำ fan-out): เพิ่มทางเลือก
"เมื่อ harness spawn subagent ได้ ให้รัน Phase 2, 3, 4 เป็น subagent คู่ขนานบน
inventory เดียวกัน แล้วรวมที่ Phase 8" แบบเดียวกับ doc2markdown — ต้องออกแบบให้
alias (`CMP/BR/TD/V/TC-NNN`) ถูก mint ที่ Phase 8 เท่านั้น จึงเป็นงานออกแบบที่ต้อง
ทดสอบด้วย scenario ก่อน ไม่ใช่แก้ข้อความอย่างเดียว

### 5.6 business-rules-extraction (1.1.0) — เนื้อหาแน่น แต่ trigger อยู่ท้าย และ reference ไม่มี TOC

ประเด็น: description วาง "Triggers on:" หลังตัวอักษรที่ ~300 (4.4); 11 ไฟล์ใน
`references/` ไม่มี TOC (4.5); ขั้นตอน 11 และ 16 เป็นย่อหน้าเดียวยาว 900+ ตัวอักษร
ซึ่งอ่านยากแต่ไม่กระทบ token; `README.md` + `LICENSE` ในโฟลเดอร์ skill ซ้ำกับ
SKILL.md บางส่วน (Amp จำกัด 200 ไฟล์ต่อ skill — เรามี 27 จึงยังห่าง)

ข้อเสนอ (patch → 1.1.1): เขียน description ใหม่ให้ trigger อยู่หน้า; เพิ่ม TOC;
แตกขั้นตอน 11/16 เป็น sub-bullet

### 5.7 codebase-analysis-report (1.1.0) — เล็กที่สุดและถูกต้อง

ไม่มีประเด็นเชิง spec; `assets/mermaid.min.js` 2.7 MB จำเป็นสำหรับ offline rendering
และไม่กิน context (ไม่ถูกอ่าน) เพิ่ม TOC ใน `references/validation.md` (115 บรรทัด)
เป็น patch เดียว

---

## 6. เทคนิคใหม่ที่ควรนำมาใช้ (เรียงตามความคุ้มค่า)

1. **`claude plugin eval` + grader `tool_used: Skill`** — วัด trigger rate และ
   pass rate พร้อม baseline ไม่มี skill ในคำสั่งเดียว แทนที่การทดสอบด้วยมือทั้งหมด
   สำหรับ Claude Code (ส่วน 4.2)
2. **`/skill-doctor` และ `/context`** — ดูต้นทุน context จริงต่อ skill และจำนวนครั้ง
   ที่ถูกเรียก ใช้ตัดสินใจว่า skill ใดควรตั้ง `skillOverrides: name-only` ใน
   settings ของผู้ใช้ (เช่น codebase-analysis-report ที่เรียกนาน ๆ ครั้ง) — เป็น
   การตั้งค่าฝั่งผู้ใช้ ไม่แตะ frontmatter จึงไม่กระทบ portability; ควรใส่คำแนะนำนี้ใน
   README
3. **กฎ 5,000 token แรก** — จัดลำดับ SKILL.md ให้คำสั่งที่ต้อง "คงอยู่ตลอดงาน" อยู่ต้นไฟล์
   เพราะ Claude Code re-attach เฉพาะส่วนนี้หลัง compaction และไม่อ่าน SKILL.md ซ้ำใน
   เทิร์นถัดไป
4. **Organise references by variant** — โหลดเฉพาะไฟล์ของชนิดงาน (doc2markdown
   ตามชนิดเอกสาร, codebase-analysis ตามภาษา ซึ่งทำอยู่แล้ว)
5. **Description-first-240** — เขียนให้ trigger ครบใน 240 ตัวอักษรแรก (ส่วน 4.4)
6. **Subagent fan-out แบบ portable** — เขียนเป็นเงื่อนไข "when your harness spawns
   subagents" ใน body (doc2markdown, init-project ทำแล้ว) แทนการใช้ `context: fork`
   ซึ่งเป็น field เฉพาะ Claude Code และทำให้ `skills-ref validate` ล้มเหลว
   (unknown key = error) — ยืนยันว่ากฎข้อ 6 ของ CLAUDE.md ยังถูกต้อง
7. **Spec freshness สำหรับ Agent Skills** — ขยาย `check-spec-versions.sh` ให้
   เปรียบเทียบ commit hash ล่าสุดของ `docs/specification.mdx` กับค่าที่บันทึกใน
   `knowledge/specs/agent-skills-spec.md` เพราะ spec ยังไม่มีเลขเวอร์ชัน

สิ่งที่ตรวจแล้ว**ไม่ควรนำมาใช้**ในรีโปนี้: `context: fork`, `paths:`, `when_to_use`,
`hooks`, `argument-hint`, `${CLAUDE_SKILL_DIR}`, `!`command`` — ทั้งหมดเป็น
Claude-Code-only; หน้า docs ของ Claude Code เองระบุว่า agent อื่นรับเฉพาะ 6 field
และ key อื่น "cause a hard packaging/upload error"

---

## 7. สิ่งที่ล้าสมัยและควรเอาออกหรือแก้

| ที่ | ข้อความปัจจุบัน | สถานะ | แก้เป็น |
|---|---|---|---|
| ทุก SKILL.md `## Updating` | "restart the agent session so the new version loads" | ล้าสมัยสำหรับ Claude Code (hot reload ตั้งแต่ 2.1.0; dir ใหม่ใช้ `/reload-skills`) | ตาม 4.3 |
| `authoring-checklist.md` Testing | ทดสอบ trigger ด้วยมือใน session ใหม่ | ถูกแทนด้วย `claude plugin eval` | ตาม 4.2 (คงไว้เป็น fallback สำหรับ agent อื่น) |
| `best-practices.md` §6 | "This repo has no eval convention of its own" | ยังจริง แต่เหตุผล ("ไม่มี tooling ในตัว") หมดไปแล้ว | เพิ่ม decision + ลิงก์ |
| `best-practices.md` §1 | "~100 tokens per skill preloaded" เท่านั้น | ไม่ครบ | เพิ่มงบ 1%/1,536 chars, ZCode 250, Kimi 240, Codex shortening |
| `agent-skills-spec.md` | "25+ agents" | เก่า | 46 clients ใน showcase; donated to AAIF 2026-10-22 |
| `creating-skills` Skill prefixes | flow ถามผู้ใช้เมื่อไม่มี plugin | ไม่เกิดในรีโปนี้อีก | ย่อ + อ้างอิง (5.4) |
| `git-commit` `allowed-tools` | YAML list | ไม่ตรง spec | string (4.7) |
| CLAUDE.md "run once: install.sh --project ." | ไม่เตือนเรื่องโหลดซ้ำกับ plugin | ขาด | เพิ่มคำเตือน (4.1) |
| `skill-discovery-matrix.md` | Gemini CLI, Kimi CLI, URL Codex | เปลี่ยนแล้ว | re-verify (4.8) |

ไม่พบ skill ใดที่ควร**ถอดออก**ทั้งตัว ทั้ง 7 ยังมีหน้าที่ชัดและไม่ซ้ำกัน

---

## 8. แผนดำเนินการที่เสนอ

ทุก release ต้องทำตามกฎข้อ 4: concept ใน `knowledge/`, `log.md`, `CHANGELOG.md`,
bump skill + `bump-version.sh`

| เฟส | งาน | เวอร์ชัน repo |
|---|---|---|
| 0 | commit งาน init-project 1.2.0 / 0.14.0 ที่ค้างอยู่ก่อน | 0.14.0 |
| 1 — ไม่แตะ skill | 4.1 (ปิดช่องทางซ้ำ + เตือนใน CLAUDE.md/install.sh), 4.6 (`license`, ลบ .DS_Store), decision `evals` layout, อัปเดต KB (4.8) | 0.14.1 (Tooling/Knowledge) |
| 2 — รูปแบบร่วม | template + `## Updating` ใหม่ทั้ง 7 skill (4.3), description ใหม่ตาม 4.4, `allowed-tools` string, TOC 14 ไฟล์ (4.5) — patch ทุก skill ที่แตะ | 0.15.0 (creating-skills minor เพราะ template/checklist เปลี่ยน) |
| 3 — eval | สร้าง `evals/` สำหรับ git-commit และ doc2markdown (trigger + anti-trigger + output), รัน `claude plugin eval` ครั้งแรก บันทึก baseline ใน KB | 0.15.1 |
| 4 — ลดขนาด | doc2markdown split by variant (1.2.0), init-project ≤ 4,000 token (1.3.0), creating-skills Skill prefixes (ภายใน 2) | 0.16.0 |
| 5 — ออกแบบ | codebase-analysis parallel phases (2.1.0) หลังเขียน scenario ทดสอบ; ขยาย `check-spec-versions.sh` ให้ตรวจ Agent Skills spec | 0.17.0 |

เฟส 1–2 ทำได้ภายในรอบเดียว เฟส 3 ต้องการ fixture (repo ตัวอย่างสำหรับ git-commit,
ไฟล์ .docx/.pdf ตัวอย่างสำหรับ doc2markdown) ซึ่งควรเป็นไฟล์ที่สร้างขึ้นเองไม่มีข้อมูลจริง

---

## 9. คำตอบของผู้ดูแล (2026-11-08)

| # | คำถาม | คำตอบ | ผลต่อแผน |
|---|---|---|---|
| 1 | License ของทั้งรีโป | **MIT** | ใส่ `"license": "MIT"` ใน plugin.json และเพิ่มไฟล์ `LICENSE` ที่ root (เฟส 1) |
| 2 | convention `evals/` และ fixture | **ใช่ — fixture สังเคราะห์** | `evals/<skill>-<case>/` ที่ root ของ plugin, fixture สร้างเองใน `evals/fixtures/` ไม่มีข้อมูลจริง, บันทึกเป็น `knowledge/decisions/2026-11-08-eval-suite-layout.md` (เฟส 1), เริ่มจาก git-commit และ doc2markdown (เฟส 3) |
| 3 | ช่องทางเมื่อทำงานในรีโปนี้ | **Symlink, ปิด plugin** | คง `.claude/skills/` ไว้; ปิด `kengjudd@kengjudd` บนเครื่องนี้; เพิ่มคำเตือนใน CLAUDE.md และ `install.sh` (เฟส 1) |
| 4 | init-project ย้าย Phase 1 ข้อ 5–9 และ Phase 4 ข้อ 2–5 ไป references | **ยอมรับ** | `references/phase-interview.md`, `references/phase-context-files.md`; เป้าหมาย body ≤ 4,000 token; bump 1.3.0 (เฟส 4) |

---

## 10. แหล่งอ้างอิง (ตรวจสอบ 2026-11-08)

Anthropic / Claude Code

- Skill authoring best practices — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (undated; `docs.claude.com` redirect 302 มาที่นี่)
- Agent Skills overview — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude Code skills (frontmatter fields, 1,536-char cap, 1% listing budget, compaction re-attach 5,000/25,000 tokens, hot reload, `/skill-doctor`) — https://code.claude.com/docs/en/skills
- Plugin evals (`claude plugin eval`, graders, 3 runs/arm, report.html) — https://code.claude.com/docs/en/plugin-evals
- Claude Code CHANGELOG (ไม่มีวันที่ มีแต่เลขเวอร์ชัน) — https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- skill-creator SKILL.md (pushy descriptions, description optimizer) — https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- Improving skill-creator (2026-03-03) — https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills
- Donating Agent Skills to the AAIF (2026-10-22) — https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation
- When to fold subagents into the main loop (2026-10-22; progressive disclosure cut system prompt >80%) — https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop

Spec และ validator

- Agent Skills specification — https://agentskills.io/specification (undated; แก้ล่าสุด 2026-08-03/04 ตาม commit history)
- Evaluating skills — https://agentskills.io/skill-creation/evaluating-skills
- skills-ref validator (unknown key = error) — https://github.com/agentskills/agentskills (`skills-ref/src/skills_ref/validator.py`)

Agent อื่น

- Codex — https://learn.chatgpt.com/docs/build-skills.md
- Cursor — https://cursor.com/docs/skills
- opencode — https://opencode.ai/docs/skills/
- Gemini CLI (updated 2026-04-30; banner Antigravity CLI) — https://geminicli.com/docs/cli/creating-skills/
- Zed — https://zed.dev/docs/ai/skills
- Amp — https://ampcode.com/docs/customize/skills
- Goose (mirror; canonical 404 ขณะตรวจ) — https://goose-docs.ai/docs/guides/context-engineering/using-skills/
- Kiro (updated 2026-10-21) — https://kiro.dev/docs/skills/
- Kimi CLI — https://moonshotai.github.io/kimi-cli/en/customization/skills.html
- ZCode (250-char excerpt, drop >1024) — https://zcode.z.ai/en/docs/skill
- Claude Code ไม่อ่าน `.agents/skills` — https://github.com/anthropics/claude-code/issues/31005

งานวิจัย

- arXiv 2602.08004 (2026-02-08): 40,285 skills, median SKILL.md 1,414 tokens — https://arxiv.org/html/2602.08004

*Unverified* ที่กล่าวถึง: issue #1721 ของ skill-creator (description loop ให้ recall 0%),
fallback 8,000 chars ของ Claude Code, project-scope path ของ ZCode
