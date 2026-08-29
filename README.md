# skills-kengjudd

**EN** — Private central repository of [Agent Skills](https://agentskills.io)
usable across multiple AI coding agents — Claude Code (primary), ZCode (Z.ai),
Codex, Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI, Amp, Goose — paired
with a project knowledge base in the
[OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) format.

**TH** — คลังกลางส่วนตัวสำหรับ [Agent Skills](https://agentskills.io) ที่ใช้ได้กับ
AI coding agent หลายตัว — Claude Code (ตัวหลัก), ZCode (Z.ai), Codex, Cursor,
opencode, Gemini CLI, Zed, Kiro, Kimi CLI, Amp, Goose — พร้อมฐานความรู้ของโปรเจกต์
ในรูปแบบมาตรฐาน [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format)

Every section below is written in English first, then Thai.
ทุกหัวข้อด้านล่างเขียนภาษาอังกฤษก่อน แล้วตามด้วยภาษาไทย

- **Agents / สำหรับ agent:** read [CLAUDE.md](CLAUDE.md) (canonical rules).
  [AGENTS.md](AGENTS.md) and [GEMINI.md](GEMINI.md) point there.
  — อ่าน [CLAUDE.md](CLAUDE.md) ซึ่งเป็นกฎฉบับหลัก ส่วน [AGENTS.md](AGENTS.md)
  และ [GEMINI.md](GEMINI.md) เป็นตัวชี้ทางมาที่ไฟล์นั้น
- **Humans / สำหรับคน:** this README — ไฟล์ README นี้

## Layout / โครงสร้างรีโป

| Path | Purpose / จุดประสงค์ |
|---|---|
| `skills/<name>/` | One skill per folder (agentskills.io spec). Every skill has its own `## Updating` command and `metadata.version`.<br>หนึ่งโฟลเดอร์ต่อหนึ่ง skill ตามสเปก agentskills.io ทุก skill มีคำสั่งอัปเดตของตัวเองในหัวข้อ `## Updating` และมี `metadata.version` |
| `knowledge/` | OKF knowledge bundle (version recorded in `knowledge/index.md`) — specs, per-agent facts, authoring playbooks, decisions.<br>ชุดความรู้รูปแบบ OKF (เวอร์ชันบันทึกไว้ใน `knowledge/index.md`) — สรุปสเปก ข้อเท็จจริงรายเครื่องมือ playbook การเขียน skill และบันทึกการตัดสินใจ |
| `scripts/` | `install.sh` (symlink into agent dirs), `update.sh` (per-skill updater), `check-spec-versions.sh` (OKF freshness), `bump-version.sh` (all four version fields at once).<br>`install.sh` (สร้าง symlink ไปยังโฟลเดอร์ skill ของแต่ละ agent), `update.sh` (อัปเดตราย skill), `check-spec-versions.sh` (ตรวจว่าสเปก OKF ยังไม่ล้าสมัย), `bump-version.sh` (ขยับเวอร์ชันทั้งสี่ฟิลด์พร้อมกัน) |
| `templates/skill-template/` | Scaffold for new skills.<br>โครงร่างตั้งต้นสำหรับสร้าง skill ใหม่ |
| `docs/` | Human design/spec documents. Not an OKF bundle and not a substitute for a `knowledge/` concept.<br>เอกสารออกแบบสำหรับคนอ่าน ไม่ใช่ OKF bundle และใช้แทนเอกสารใน `knowledge/` ไม่ได้ |
| `.claude-plugin/` | Claude Code plugin + marketplace packaging.<br>ไฟล์แพ็กเกจ plugin และ marketplace ของ Claude Code |

## Install / การติดตั้ง

**EN** — Clone the repo, then link the skills into the skill directory of the
agent you use. The repo is private, so cloning requires working git auth.

**TH** — clone รีโปนี้ แล้วสร้างลิงก์ skill ทั้งหมดไปยังโฟลเดอร์ skill ของ agent
ที่ใช้งาน รีโปนี้เป็น private การ clone จึงต้องตั้งค่า git auth ไว้เรียบร้อยก่อน

```bash
git clone git@github.com:gitkeng/skills-kengjudd.git
cd skills-kengjudd

# Link every skill into an agent's skill directory (user scope)
# ลิงก์ทุก skill เข้าโฟลเดอร์ของ agent ในระดับผู้ใช้
./scripts/install.sh --tool claude    # ~/.claude/skills
./scripts/install.sh --tool codex     # ~/.agents/skills (also cursor|opencode|gemini|zed|goose)
./scripts/install.sh --tool kimi      # ~/.config/agents/skills (also amp)
./scripts/install.sh --tool kiro      # ~/.kiro/skills
./scripts/install.sh --tool zcode     # ~/.zcode/skills
./scripts/install.sh --tool all       # all of the above / ทั้งหมดข้างต้น

# Or per project / หรือติดตั้งเฉพาะโปรเจกต์
./scripts/install.sh --tool claude --project /path/to/project
```

**EN** — Claude Code alternative (plugin marketplace):

**TH** — ทางเลือกสำหรับ Claude Code (ติดตั้งผ่าน plugin marketplace):

```text
/plugin marketplace add gitkeng/skills-kengjudd
/plugin install skills-kengjudd@kengjudd
```

**EN** — Because the repo is private, the marketplace add needs working git
auth. The `owner/repo` shorthand clones over SSH by default; for HTTPS-only
setups set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` or add it by SSH URL
(`/plugin marketplace add git@github.com:gitkeng/skills-kengjudd.git`).

**TH** — เนื่องจากรีโปเป็น private การ add marketplace ต้องมี git auth ที่ใช้งานได้
รูปแบบย่อ `owner/repo` จะ clone ผ่าน SSH เป็นค่าเริ่มต้น หากเครื่องตั้งค่าไว้เฉพาะ
HTTPS ให้กำหนด `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` หรือระบุเป็น SSH URL แทน
(`/plugin marketplace add git@github.com:gitkeng/skills-kengjudd.git`)

## Update / การอัปเดต

**EN** — Each skill documents its own update command in its SKILL.md
`## Updating` section, for both install channels.

**TH** — ทุก skill ระบุคำสั่งอัปเดตของตัวเองไว้ในหัวข้อ `## Updating` ของ SKILL.md
ครอบคลุมช่องทางติดตั้งทั้งสองแบบ

```bash
# git clone + symlink installs / ติดตั้งแบบ clone แล้ว symlink
./scripts/update.sh <skill-name>   # one skill: fetch → compare version → show changes → pull
                                   # ทีละ skill: fetch → เทียบเวอร์ชัน → แสดงสิ่งที่เปลี่ยน → pull
./scripts/update.sh --all          # every skill / ทุก skill
```

```bash
# Claude Code plugin installs (the plugin cache has no .git)
# ติดตั้งแบบ plugin ของ Claude Code (แคชของ plugin ไม่มี .git จึงใช้ update.sh ไม่ได้)
claude plugin update skills-kengjudd@kengjudd
```

## Creating a new skill / การสร้าง skill ใหม่

**EN** — Invoke the `creating-skills` skill from any supported agent, or read
[skills/creating-skills/SKILL.md](skills/creating-skills/SKILL.md) — it covers
naming, frontmatter, structure, registration, knowledge capture, and versioning.

**TH** — เรียกใช้ skill ชื่อ `creating-skills` จาก agent ตัวใดก็ได้ที่รองรับ หรืออ่าน
[skills/creating-skills/SKILL.md](skills/creating-skills/SKILL.md) โดยตรง —
ครอบคลุมการตั้งชื่อ frontmatter โครงสร้างไฟล์ การลงทะเบียน skill การบันทึกความรู้
และการจัดการเวอร์ชัน

## Skills / รายการ skill

| Skill | Version | Description / คำอธิบาย |
|---|---|---|
| [creating-skills](skills/creating-skills/SKILL.md) | 1.1.0 | Meta-skill: create, update, and register skills in this repo.<br>skill แม่แบบ: สร้าง อัปเดต และลงทะเบียน skill ในรีโปนี้ |
| [business-rules-extraction](skills/business-rules-extraction/SKILL.md) | 1.0.0 | Statically extract, document, and verify business rules from any codebase, with line-level evidence and a mechanical validator.<br>สกัด จัดทำเอกสาร และตรวจสอบ business rule จากโค้ดเบสใด ๆ แบบอ่านอย่างเดียว พร้อมหลักฐานระดับบรรทัดและตัวตรวจสอบอัตโนมัติ |
| [comprehensive-codebase-analysis](skills/comprehensive-codebase-analysis/SKILL.md) | 1.0.0 | Offline, evidence-backed analysis of any repo: architecture, behavior, security, tech debt, migration readiness, onboarding. Resumable.<br>วิเคราะห์รีโปแบบออฟไลน์โดยอ้างอิงหลักฐานจากโค้ด: สถาปัตยกรรม พฤติกรรม ความปลอดภัย หนี้ทางเทคนิค ความพร้อมย้ายระบบ และเอกสารรับคนเข้าทีม ทำต่อจากจุดที่ค้างไว้ได้ |
| [codebase-analysis-report](skills/codebase-analysis-report/SKILL.md) | 1.0.0 | Render a `comprehensive-codebase-analysis` v2 output tree into one portable, offline, accessible HTML report. Requires that skill's output as input.<br>แปลงผลลัพธ์ v2 ของ `comprehensive-codebase-analysis` เป็นรายงาน HTML ไฟล์เดียว เปิดออฟไลน์ได้ และรองรับการเข้าถึง ต้องใช้ผลลัพธ์ของ skill ตัวนั้นเป็นอินพุต |
