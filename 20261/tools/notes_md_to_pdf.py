#!/usr/bin/env python3
"""notes_md_to_pdf.py - render a lecture-notes .md file to an A4 PDF (next to it) with headless Chrome.
Usage: python3 tools/notes_md_to_pdf.py "Module 2.1 - LLMs and Reasoning/Module2_LLMs_and_Reasoning_notes.md"
Needs: pip install markdown ; google-chrome. Images are resolved relative to the .md file."""
import subprocess, sys, tempfile
from pathlib import Path
import markdown

CSS = """
@page { size: A4; margin: 16mm 15mm; }
body { font-family: Calibri, 'Open Sans', Arial, sans-serif; font-size: 10pt; color: #2F343B; line-height: 1.45; }
h1 { font-family: Cambria, Georgia, serif; color: #493347; font-size: 20pt; margin: 0 0 8pt; }
h2 { font-family: Cambria, Georgia, serif; color: #493347; background: #F7F3F7; border-left: 3px solid #C8ABC3;
     padding: 5pt 8pt; font-size: 13pt; margin: 16pt 0 6pt; break-after: avoid; }
h3 { color: #356B8C; font-size: 11.5pt; margin: 10pt 0 4pt; break-after: avoid; }
img { max-width: 78%; max-height: 70mm; object-fit: contain; display: block; margin: 6pt auto; break-inside: avoid; }
em { color: #56616D; }
code { background: #F5EDF4; padding: 0 3px; border-radius: 3px; font-size: 9.5pt; }
pre { background: #F7F3F7; padding: 8pt; border-radius: 4px; overflow-wrap: anywhere; white-space: pre-wrap; }
table { border-collapse: collapse; width: 100%; } td, th { border: 1px solid #C8ABC3; padding: 3pt 6pt; }
blockquote { background: #F5EDF4; border-left: 3px solid #A83296; margin: 8pt 0; padding: 4pt 10pt; }
"""

def main(md_path):
    md = Path(md_path).resolve()
    body = markdown.markdown(md.read_text(encoding="utf-8"), extensions=["tables", "fenced_code", "sane_lists"])
    html = f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>{body}'
    tmp = md.with_suffix(".tmp.html")  # next to the .md so relative image paths work
    tmp.write_text(html, encoding="utf-8")
    try:
        subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={md.with_suffix('.pdf')}", tmp.as_uri()], check=True, capture_output=True)
    finally:
        tmp.unlink(missing_ok=True)
    print("wrote", md.with_suffix(".pdf"))

if __name__ == "__main__":
    main(sys.argv[1])
