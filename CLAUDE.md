# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Info

- **Owner:** lshorace227-dotcom
- **Email:** lshorace227@gmail.com
- **Purpose:** Archive Claude Code session outputs, scripts, and generated files
- **Repo:** https://github.com/lshorace227-dotcom/Claude-Code

## What This Repository Is

An archive of deliverables produced in Claude Code sessions — equity research reports, daily news digests, financial documents, and one-off HTML tools. It is **not** a software project: there is no build system, test suite, linter, or CI. Each top-level directory is a self-contained session output.

### Structure

- `pdd-initiation-coverage/`, `pdd-earnings-update-q1-2026/`, `atat-earnings-update-q1-2026/` — Equity research reports: Python build scripts plus committed DOCX/XLSX/PNG outputs
- `macau-news/` — Daily Macau news digests, one Markdown file per day named `YYYY-MM-DD.md`
- `haitong-interview-prep/` — Interview prep handbook (HTML source of truth + PDF built via `build_pdf.py`)
- `ctl/`, `investment/` — Markdown records (conversation transcript, investment proposal)
- `countdown-timer.html` — Standalone HTML tool
- `skills-lock.json` / `.agents/skills/` — Pinned Claude Code skills (currently `frontend-design` from anthropics/skills)

## Conventions

### New deliverables

- Put each new project in its own kebab-case top-level directory (e.g. `pdd-earnings-update-q1-2026`).
- Generated artifacts (DOCX, PDF, PNG, XLSX) are **committed**, not gitignored — the outputs are the point of the repo.
- Commit messages follow conventional-commit style with descriptions typically in Traditional Chinese, e.g. `feat: 澳門每日新聞摘要 2026-06-05`.

### Research report pipeline

The equity-research directories share a two-step pattern:

1. `python3 generate_charts.py` — matplotlib (`Agg` backend), writes 300 DPI PNGs to `./charts/`
2. `python3 build_report.py` — python-docx, embeds the charts and writes the DOCX

Scripts resolve paths relative to `__file__`, so they run from any working directory. Chinese-language variants use a `_zh` suffix (`build_report_zh.py`, `charts_zh/`). Dependencies: `python-docx`, `matplotlib`, `numpy`; `reportlab` for PDFs.

### CJK / PDF output

LibreOffice, Chromium, and WeasyPrint are unavailable in this environment. Build CJK-capable PDFs with reportlab, registering the WenQuanYi font: `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` (see `haitong-interview-prep/build_pdf.py`).

### Macau news digests

Files in `macau-news/` follow a fixed format: Traditional Chinese, title `# 📰 澳門每日新聞摘要 — YYYY年MM月DD日`, a source attribution blockquote, then emoji-headed topic sections (🏛️ 政治/行政, etc.) where each story has a bolded bracketed headline, bullet-point details, and a `🔗 [閱讀全文](url)` source link.

---

# Behavioral Guidelines

Guidelines to reduce common LLM coding mistakes. **Tradeoff:** these bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
