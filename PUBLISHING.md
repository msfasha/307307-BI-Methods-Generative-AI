# Publishing the course website (20261)

Students use <https://msfasha.github.io/307307-BI-Methods-Generative-AI/>.
Only the current semester folder (`20261/`) is published. Older semesters are not.

## How it works

- `20261/site/build.py` stages the teaching files, runs `quarto render`, and zips the downloads.
  It never edits the teaching sources. Output goes to `20261/_build/site/` (gitignored).
- `.github/workflows/publish-course.yml` runs the build on GitHub and deploys to GitHub Pages.
  It runs on every push to `main` that touches `20261/**`, or manually (Actions tab > Run workflow).
- One-time setup (done): repo Settings > Pages > Source = **GitHub Actions**.
- Quarto is only a Markdown/notebook-to-HTML converter here. No R is used and no code is executed
  (`execute: enabled: false`), so labs show saved outputs only.

## README link (keep this)

The top of the repository `README.md` must keep a link that opens the course website, right under the title,
as in the Applied Statistics repo:

```md
[Open the student course website](https://msfasha.github.io/307307-BI-Methods-Generative-AI/) (current semester, 20261).
```

When starting a new semester, update this link text and the `SRC`/paths in `20261/site/build.py` and the workflow.
Also set the repository "Website" field (the gear next to About on the repo home page) to the same URL.

Preview locally: `python3 20261/site/build.py`, then open `20261/_build/site/index.html`.

## What each module folder must contain

Files are found by name suffix, so keep these names:

| File | Becomes |
|---|---|
| `*_notes.md` (+ `img/`) | Lecture notes (HTML) |
| `*_notes.pdf`, `*_slides.pdf`, `*_activity.pdf` | PDF links and the PDF zip |
| `*.ipynb` | Lab (HTML) and notebook download |
| `*.csv`, `*.txt`, `support files/` | Lab data, included in the notebooks zip |
| `extended/*.pdf` | "Extended lecture notes (PDF)" links (not in the PDF zip, they are large) |

PPTX/DOCX are gitignored, so they never reach the site. Folders starting with `skip_` are ignored.
To add or rename a module, edit the `MODULES` list at the top of `build.py`.
Extended slides for modules without a natural match (Evaluating Agents, Multi-Agent, Multi-Modal,
Code Agents) live under Module 6 `extended/`.

## Theme (keep this)

Petra burgundy `#7a1f3d` on Quarto's `cosmo` theme: headings and links burgundy, navbar burgundy
with **white** links, search icon included. All of it is in `20261/site/styles.css`. Layout: homepage lists modules under
"Agentic AI" and "AI Governance", then Downloads (labs zip, PDFs zip, GitHub link); each module has
its own page of links.

## Before you publish

Notebooks and notes become public. Check for API keys first (placeholders like `YOUR_GEMINI_API_KEY` are fine).
