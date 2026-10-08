# Shiji · A High-School-to-Career Mentor for Your AI Assistant

> "Climb one step at a time — both feet firm on each, then step again."
> — *Book of Rites* (《礼记·曲礼》), origin of the name 拾级

[中文 README](README.md)

**Shiji (拾级, "climbing step by step")** is a free, open-source skill pack that turns
any capable AI assistant into a mentor for Chinese students and young professionals —
covering the full journey from **gaokao (college entrance exam) application** through
university, grad school, and the first years of work.

Install it, then just ask in Chinese: *"帮我改简历"*, *"室友半夜打游戏怎么办"*,
*"考研还是找工作"* — it routes to the right guide and answers with concrete,
usable steps, not vague advice.

## What's inside

| Line | Covers |
|------|--------|
| 高考 Gaokao | Subject choice, application rules (parallel preferences, rejection mechanics), school/major selection, special admissions, retake decisions |
| 大学 University | GPA, changing major, minors & double degrees, scholarships, academic warning, competitions, campus health insurance |
| 考研 Grad-school exam | Decide, choose schools, plan, register, retake decisions, interviews & transfers, **recommendation-based admission (推免)**, college-to-degree upgrade |
| 考公 Civil service | National/provincial exams vs. selective recruitment, post selection, aptitude & essay tests, civil-service interviews, background check & medical |
| 求职 Job | Résumés (14 guides + 8 print-ready HTML templates + an application tracker), interviews, negotiation, **tripartite agreement & social insurance** |
| 职场 Workplace | First 90 days, managing up, onboarding compliance, probation & performance, social insurance rights, **frontline/blue-collar roles** |
| 人际关系 Relationships | Roommates, classmates, advisors, clubs, friendship |
| 论文 Thesis | Topic selection, literature search (CNKI), proposal, research methods, data, plagiarism/AIGC checks, defense, post-graduation audits |
| 学习 Study | Learning science, methods by subject, exams, CET-4/6, using AI to study |
| 研究生 Grad life | Three-year rhythm, research basics, publishing & authorship, lab dynamics, PhD applications |
| 留学 Study abroad | Applications, IELTS/TOEFL, visas, campus life abroad, career paths, portfolio for arts |
| 生活 Life | Money, part-time jobs, time management, mental well-being, **first apartment rental** |
| 特殊通道 Special paths | Military service, students with disabilities, Hong Kong/Macau/Taiwan students, preparatory programs, adult education |

Plus: a **cross-path roadmap**, a **reference & sources system**, an **information
literacy guide** (how to search, how to judge sources), and an **18-question
self-test** to verify your installation.

**12 lines, 151 guides** — from gaokao to the workplace.

## Design principles

- **Answers you can act on** — every reply ends with "the first thing you can do today/tonight"
- **Scripts as finished sentences** — exact words you can send, not adjectives
- **Dual-source answers** — built-in knowledge × live web search for time-sensitive info,
  **and region-aware search** (social-insurance rates, upgrade-exam policies and civil-service
  postings differ by province; a national figure is no answer)
- **Honest by design** — says "not sure" when unsure; official sources win
- **Red lines** — never writes essays for students, never diagnoses, never looks people up

## Install

**Doubao (豆包) and other AI assistants** — say this to the assistant:

> Please download and install https://github.com/ZhongQuinnKing/shiji as a skill

Or drag-and-drop: download the ZIP (Code → Download ZIP), unzip, and upload the folder
via the assistant's "Skills" panel.

**Claude Code / Codex (command line):**

```bash
git clone https://github.com/ZhongQuinnKing/shiji ~/.claude/skills/shiji
```

## Family

- [Caishi (采诗)](https://github.com/ZhongQuinnKing/caishi) — a capability pack that
  lets AI assistants read 33+ Chinese platforms
- [Yesong (夜诵)](https://github.com/ZhongQuinnKing/yesong) — an offline information
  sentinel that watches the world while your AI sleeps

## License

Dual-licensed:
- **Content** (guides, templates, preview page): **CC BY-NC-ND 4.0**.
  **Modifying it privately, for your own use (no publishing or sharing): fully
  unrestricted** — no permission, no credit required. Free to read, learn, and
  share unchanged (with attribution). **Publishing a MODIFIED version
  (non-commercial): prior permission is required** — there is no
  "attribute-and-publish" alternative. **Commercial use — modified or not —
  always requires contacting us to negotiate a paid license. No exceptions.**
  Open an issue titled 【商用授权】/【改编授权】 to get in touch.
- **Code** (`scripts/`): MIT.
- The "Shiji / 拾级" name and brand are not granted by these licenses.

Content is written from scratch — teaching cases are fictional or adapted.

*The project is Chinese-first (the audience is Chinese students). This README is a
courtesy summary for non-Chinese readers.*
