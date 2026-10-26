# Handoff Brief — 307307 Course, Governance Half (to build next)

**Purpose:** everything a fresh session needs to build the **AI Governance half** of the course in the same style as the finished **Agentic AI half**. Read this first, then confirm scope with the professor before mass-producing.

---

## 1. Who / what this is
- **Course:** 307307 "BI Methods for Generative AI", University of Petra.
- **Professor:** teaches intro courses; students are **introductory level with NO prior knowledge** and are **not strong in Python**.
- **Course shape:** two halves — **Agentic AI (DONE)** and **AI Governance (TO BUILD)**.
- **Working semester folder (on the professor's computer, via the device bridge):**
  `/mnt/mywork/active/3_education/university_courses/307307-BI-Methods-Generative-AI/20261/`

## 2. Time budget (decides scope)
- **10 teaching weeks, ~20 lectures total.** Agentic half used ~10 lectures. **Governance half gets the other ~10 lectures (~5 weeks).**
- Rhythm that worked: **one topic = one lecture + one activity session = 2 slots.** So aim for **~5 governance modules** (+ optional short survey), NOT more. Do not over-scope.

## 3. Reference book for this half
- `/.../skip_books/0_2026 AI Governance in Practice Build with 42001 (Hemang Doshi).pdf` (~21 MB). Built around **ISO/IEC 42001** (the AI Management System standard).
- **First step in the new session:** extract its table of contents / chapter structure (same technique as below) and map chapters → ~5 modules. Verify the real structure against the book; do not assume.
- Likely 42001 scaffold to expect (confirm against the book): AI Management System (AIMS) context & scope · leadership & policy · **AI risk assessment & AI impact assessment** · Annex A controls · operation & the **AI system lifecycle** · roles/responsibilities & data governance · performance evaluation, audit & continual improvement. Also weave in the broader governance themes the agentic half already seeded: **human-in-the-loop, guardrails, hallucinations/reliability, evaluation (outcome vs trajectory)**.

## 4. IMPORTANT format difference: governance is non-coding
- The agentic half's hands-on piece was a **Jupyter notebook**. Governance has **no code**. Replace the notebook with a **non-coding activity per module**: a worksheet / case study / checklist / role-play / mini risk-or-impact-assessment the students fill in. Keep it **gentle and concrete** (a real-ish scenario — e.g. a university chatbot, a hiring screener, a medical triage assistant — carried through the module).
- Deliver these activities as a **document** (`.md`, or a fillable `.docx`/PDF if the professor prefers a handout). Ask the professor which activity format they want before building all five.

## 5. The per-module deliverable set (mirror the agentic half)
For each module, produce three files:
1. **Lean deck** — PowerPoint `.pptx`, **~12–15 slides**, built with `pptxgenjs`.
2. **Activity** — the non-coding worksheet/case study (see §4).
3. **One-page notes** — `.md` with objectives, plain-language concepts, a real-world example, common misconceptions, summary, review questions; **book figures embedded** (relative `img/` refs + an `img/` folder shipped alongside).

**Folder layout convention** (match agentic half exactly):
`20261/Module N - <Short Name> (compiled)/` containing the `.pptx`, the activity file, `*_notes.md`, and an `img/` subfolder.

## 6. THE STYLE SCHEME (must match — files already in the repo)
The professor's approved scheme lives at **`20261/assets/petra-brand.css`** and **`20261/assets/STYLE_GUIDE.md`** — read them. Quiet surfaces, dark text, restrained Petra branding. Exact palette to reuse in decks:

| Role | Hex |
|---|---|
| Heading / primary accent (dark plum) | `#493347` |
| Petra brand purple — **thin accents only** (title top rule, small chip) | `#A83296` |
| Title panel surface (pale lavender) | `#F5EDF4` |
| Section/card surface (light lavender) | `#F7F3F7` |
| Muted left-rule accent | `#C8ABC3` |
| Body text | `#2F343B` |
| Secondary / captions | `#56616D` |
| Links / muted-blue secondary accent | `#356B8C` |
| Muted secondary accents (for chips) | plum `#493347`, blue `#356B8C`, teal `#5E8390`, mauve `#8A6884`, rose `#9C5A6E` |
| Table header `#F3F4F6` · divider `#DEE2E6` · code surface `#F3F4F6` · note surface `#EFF4F7` / rule `#6C91A8` |

Rules: **no large saturated purple panels**, `#D070D0` is retired, white space dominates. **Book figure excerpts keep their ORIGINAL colors and attribution** (never recolor them). Fonts: Cambria (headings) + Calibri (body), both safe. Charts (if any) use analytical colors, not forced purple.

**Reusable pptxgenjs deck skeleton** (copy the exact constants/helpers from any agentic `build_deck.js`, e.g. `307307_Module5_Planning_ReAct/build_deck.js` in the session outputs, or re-derive): LAYOUT_WIDE (13.333×7.5), `slide()`, `title()` (small `#A83296` chip + plum text), `card()` (lavender fill), `chip()` (muted fill, white number), `imgFit()`, `caption()`. Title slide = pale-lavender panel (`#F5EDF4`) with a 3px `#A83296` top rule, plum title, muted subtitle, course meta on white below, book cover on the right. Key Takeaways + Discussion as closing slides. Keep decks **printer-friendly** (no full-bleed color pages — the professor explicitly asked).

## 7. Build toolchain & mechanics (what worked)
- **Figures from the book:** stage the PDF, find chapter pages by searching the extracted text, rasterize figure pages with `pdftoppm -png -r 130 -f P -l P`, then crop with Pillow. Repo images aren't available for this book (it's a plain PDF), so all figures come from rasterizing the PDF. Add an attribution caption: *"Figure from AI Governance in Practice (Hemang Doshi, 2026)."* (confirm exact title/year from the PDF).
- **Decks:** write `build_deck.js`, `node build_deck.js`, then **validate** `python3 /mnt/skills/public/pptx/scripts/office/validate.py deck.pptx`, then **visual QA** via `soffice.py --convert-to pdf` + `pdftoppm` + Read the images. Fix overflow/empty-bullet issues before delivering.
- **pptx skill:** `/mnt/skills/public/pptx/SKILL.md` (gotchas: hex without `#`, set layout before slides, `bullet:true` per item without trailing `\n`, speaker notes via `addNotes`, etc.).
- **university-teaching-material skill** is available and tuned to this professor (Petra brand), but its default is bright `#A83296` panels — **override with the quiet scheme above.**
- **Notes figures embedded in activities/notebooks** (if any HTML) via base64; notes `.md` use relative `img/` refs with the folder shipped alongside.
- **Delivery to the professor's computer:** `mcp__remote-devices__device_stage_files` to read source files; `device_commit_files` to write deliverables into the `20261` folders (use `force:true` when overwriting). Build in `/mnt/user-data/outputs/` first, QA, then commit.

## 8. Agentic half — what's already done (for continuity / tone)
Five modules in `20261`, each a `(compiled)` folder with deck + notebook + notes + `img/`:
- **M1** What is an AI Agent · **M2** LLMs & Reasoning · **M3** Memory · **M4** Tools & MCP · **M5** Planning & ReAct (+ a closing "Beyond a Single Agent" survey).
- Pedagogy: **intuition-first, gentle, run-and-observe**, built on the book *An Illustrated Guide to AI Agents* and (for labs) the free **Google Gemini** API. The governance half should feel like a natural continuation — several governance themes (human-in-the-loop, guardrails, hallucinations, evaluation) were deliberately seeded there.

## 9. First actions for the new session
1. Confirm with the professor: **how many governance modules** (suggest 5) and **what activity format** (worksheet `.md` vs fillable handout).
2. Read `20261/assets/STYLE_GUIDE.md` + `petra-brand.css`.
3. Extract the governance book's TOC and propose a 5-module map for approval.
4. Build **one pilot module** end-to-end, get sign-off on the format, then scale — exactly how the agentic half was done.

## 10. Open items to flag
- Notebook/deck **model id** (`gemini-3.8-flash`) and live runs in the agentic labs were **not tested against a real key** — professor to verify before class (not relevant to governance, which is code-free).
- Offer (optional): styled **HTML versions of the notes** using `petra-brand.css`, if the professor wants them to render in the scheme outside a plain Markdown viewer.
