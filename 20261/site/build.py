#!/usr/bin/env python3
"""Build the 20261 course website: stage sources -> quarto render -> zip bundles.

Run from anywhere:  python3 20261/site/build.py
Output: 20261/_build/site/   (never modifies the teaching sources)
"""
from urllib.parse import quote
import json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent                      # 20261/
STAGE = SRC / "_build" / "stage"
OUT = SRC / "_build" / "site"
REPO_URL = "https://github.com/msfasha/307307-BI-Methods-Generative-AI"

# (slug, folder, title, part)
MODULES = [
    ("module-1", "Module 1 - What is an AI Agent", "What is an AI Agent", "Agentic AI"),
    ("module-2-1", "Module 2.1 - LLMs and Reasoning", "LLMs and Reasoning", "Agentic AI"),
    ("module-2-2", "Module 2.2 - Accessing LLMs thought APIs", "Accessing LLMs through APIs", "Agentic AI"),
    ("module-3", "Module 3 - Memory", "Memory", "Agentic AI"),
    ("module-4", "Module 4 - Tools and MCP", "Tools and MCP", "Agentic AI"),
    ("module-5", "Module 5 - Planning and ReAct", "Planning and ReAct", "Agentic AI"),
    ("module-6", "Module 6 - Introduction to CrewAI", "Introduction to CrewAI", "Agentic AI"),
    ("module-7", "Module 7 - Foundations of AI Governance", "Foundations of AI Governance", "AI Governance"),
    ("module-8", "Module 8 - The Rules Landscape", "The Rules Landscape", "AI Governance"),
    ("module-9", "Module 9 - ISO 42001 and Governance Structure", "ISO 42001 and Governance Structure", "AI Governance"),
    ("module-10", "Module 10 - AI Impact and Risk Assessment", "AI Impact and Risk Assessment", "AI Governance"),
    ("module-11", "Module 11 - Lifecycle, Incidents and Audit", "Lifecycle, Incidents and Audit", "AI Governance"),
]

def stage_for_html(src, dst):
    """Copy a notebook for rendering, dropping the 'Open in Colab' badge cell (raw HTML shows as code on the site)."""
    nb = json.loads(src.read_text(encoding="utf-8"))
    nb["cells"] = [c for c in nb["cells"] if "colab-badge.svg" not in "".join(c.get("source", []))]
    dst.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

def find(folder, suffix):
    return sorted(p for p in folder.iterdir() if p.is_file() and p.name.endswith(suffix)
                  and not p.name.startswith(".~lock"))

def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    STAGE.mkdir(parents=True)
    shutil.copy(HERE / "_quarto.yml", STAGE / "_quarto.yml")
    shutil.copy(HERE / "styles.css", STAGE / "styles.css")
    nb_bundle, pdf_bundle, cards = [], [], {}

    for slug, folder, title, part in MODULES:
        s = SRC / folder
        d = STAGE / slug
        d.mkdir()
        links = {}   # label -> [(format text, href)]; same item in several formats is listed on one line
        add = lambda label, fmt, href: links.setdefault(label, []).append((fmt, href))
        notes = find(s, "_notes.md")
        if notes:
            shutil.copy(notes[0], d / "notes.md")
            # front matter so quarto titles the page; keep the original H1 out of the way
            text = (d / "notes.md").read_text(encoding="utf-8")
            text = re.sub(r"\A# .*\n", "", text, count=1)
            (d / "notes.qmd").write_text(f'---\ntitle: "Module notes: {title}"\ntoc: true\n---\n\n{text}', encoding="utf-8")
            (d / "notes.md").unlink()
            if (s / "img").is_dir():
                shutil.copytree(s / "img", d / "img")
            add("Lecture notes", "HTML", "notes.html")
        for kind, suffix in (("Lecture notes", "_notes.pdf"), ("Slides", "_slides.pdf"),
                             ("Activity", "_activity.pdf")):
            for p in find(s, suffix):
                shutil.copy(p, d / p.name)
                add(kind, "PDF", p.name)
                pdf_bundle.append((p, f"{slug}/{p.name}"))
        # extended lecture slides (module/extended/*.pdf) -> own links, kept out of the PDF zip (large)
        for p in sorted((s / "extended").glob("*.pdf")) if (s / "extended").is_dir() else []:
            (d / "extended").mkdir(exist_ok=True)
            shutil.copy(p, d / "extended" / p.name)
            add(f"Extended lecture notes: {p.stem.replace('_', ' ')}", "PDF", f"extended/{p.name}")
        for p in sorted(s.glob("*.ipynb")):
            stage_for_html(p, d / p.name)   # rendered copy has no Colab badge; the download copy keeps it
            nbq = p.name
            lab = "Lab" if len(list(s.glob("*.ipynb"))) == 1 else f"Lab: {p.stem.replace('_', ' ')}"
            add(lab, "HTML", p.stem + ".html")
            # browsers show a raw .ipynb as JSON text, so link to GitHub, which renders notebooks
            add(lab, "Notebook (.ipynb)", f"{REPO_URL}/blob/main/{SRC.name}/{folder}/{p.name}")
            nb_bundle.append((p, f"{slug}/{p.name}"))
        # lab data / support files
        extra = [p for p in s.iterdir() if p.is_file() and p.suffix in (".csv", ".txt")]
        for p in extra:
            shutil.copy(p, d / p.name)
            nb_bundle.append((p, f"{slug}/{p.name}"))
        if (s / "support files").is_dir():
            shutil.copytree(s / "support files", d / "support files")
            for p in (s / "support files").rglob("*"):
                if p.is_file():
                    nb_bundle.append((p, f"{slug}/support files/{p.relative_to(s / 'support files')}"))
        cards[slug] = (title, part, links)

    # homepage + per-module pages
    def mod_page(slug, title, part, links):
        def row(label, fmts):
            if label.startswith("Extended"):          # single format: the whole line is the link
                name = label.split(": ", 1)[1]
                return f"- [{name} (PDF)]({quote(fmts[0][1], safe=':/')})"
            return f"- {label}: " + " · ".join(f"[{f}]({quote(h, safe=':/')})" for f, h in fmts)
        main = [row(l, f) for l, f in links.items() if not l.startswith("Extended")]
        extended = [row(l, f) for l, f in links.items() if l.startswith("Extended")]
        body = "\n".join(main) + "\n"
        if extended:   # optional material is set apart so students do not confuse it with the formal material
            body += ("\n---\n\n## Optional: extended lecture notes\n\n"
                     "*Extra reading for those who want to go deeper. Not required for the course.*\n\n"
                     + "\n".join(extended) + "\n")
        (STAGE / slug / "index.qmd").write_text(
            f'---\ntitle: "{title}"\n---\n\n{body}', encoding="utf-8")
    sections = {}
    for slug, (title, part, links) in cards.items():
        mod_page(slug, title, part, links)
        num = slug.replace("module-", "").replace("-", ".")
        sections.setdefault(part, []).append(f"- [Module {num} - **{title}**]({slug}/index.qmd)")
    body = ["---", 'title: "307307 BI Methods for Generative AI"',
            'subtitle: "First semester 2025/2026 (20261) - Agentic AI and AI Governance"', "toc: false", "---", ""]
    for part, items in sections.items():
        body += [f"## {part}", ""] + items + [""]
    body += ["## Downloads", "",
             "- [Download all labs and data (.zip)](downloads/genai-labs-notebooks.zip)",
             "- [Download all PDFs: notes, slides, activities (.zip)](downloads/genai-course-pdfs.zip)",
             f"- [Source on GitHub]({REPO_URL})", ""]
    (STAGE / "index.qmd").write_text("\n".join(body), encoding="utf-8")

    # zips go in the stage so quarto copies them as resources
    dl = STAGE / "downloads"
    dl.mkdir()
    readme = "Run labs in Jupyter/VS Code/Colab. Each folder = one module. API keys: see module 2.2 support files.\n"
    for name, files in (("genai-labs-notebooks.zip", nb_bundle), ("genai-course-pdfs.zip", pdf_bundle)):
        with zipfile.ZipFile(dl / name, "w", zipfile.ZIP_DEFLATED) as z:
            for p, arc in files:
                z.write(p, arc)
            if "notebooks" in name:
                z.writestr("README.txt", readme)

    subprocess.run(["quarto", "render"], cwd=STAGE, check=True)
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.move(str(STAGE / "_site"), OUT)
    print("Built ->", OUT)

if __name__ == "__main__":
    sys.exit(main())
