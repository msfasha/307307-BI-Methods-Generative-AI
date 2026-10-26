#!/usr/bin/env python3
"""
convert_to_pdf.py - batch-convert .docx / .pptx files to PDF with LibreOffice.

Reusable: point it at any folder tree. By default it converts everything under
the folder that contains this script's parent directory (i.e. if this file is
<course>/tools/convert_to_pdf.py, the root is <course>), and writes each PDF
next to its source file.

Rules (so re-running is cheap and safe):
  * A PDF that already exists and is newer than its source is skipped.
    Use --force to rebuild everything.
  * Anything with "skip" in a file or folder name is ignored (your convention
    for old versions). Use --include-skip to convert those too.
  * Office lock/temp files (~$..., .~lock...) and hidden folders are ignored.
  * Existing PDFs are never deleted. A PDF is only replaced after the new one
    has been converted successfully.

Requirements: Python 3.8+ and LibreOffice (the `soffice` command).
  Linux:   sudo apt install libreoffice-impress libreoffice-writer
  macOS:   brew install --cask libreoffice
  Windows: install LibreOffice; this script finds soffice.exe automatically.

Examples:
  python3 tools/convert_to_pdf.py                 # convert the whole course
  python3 tools/convert_to_pdf.py --dry-run       # just list what would run
  python3 tools/convert_to_pdf.py "Module 3 - Memory"      # one folder
  python3 tools/convert_to_pdf.py --only pptx     # slides only
  python3 tools/convert_to_pdf.py --outdir ~/pdf_out        # mirror into another folder
  python3 tools/convert_to_pdf.py --force         # rebuild all PDFs
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXTS = {".docx": "docx", ".pptx": "pptx"}


def find_soffice(explicit=None):
    cands = [explicit] if explicit else []
    cands += ["soffice", "libreoffice"]
    for c in cands:
        if c and shutil.which(c):
            return shutil.which(c)
    for p in (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ):
        if os.path.exists(p):
            return p
    return None


def is_ignored(rel_parts, name, include_skip):
    if name.startswith("~$") or name.startswith(".~lock"):
        return True
    if any(p.startswith(".") for p in rel_parts):
        return True
    if not include_skip:
        if "skip" in name.lower() or any("skip" in p.lower() for p in rel_parts):
            return True
    return False


def collect(root, only, include_skip):
    wanted = {e for e, k in EXTS.items() if only in (None, k)}
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root).parts
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for fn in sorted(filenames):
            if Path(fn).suffix.lower() in wanted and not is_ignored(rel, fn, include_skip):
                found.append(Path(dirpath) / fn)
    return found


def pdf_pages(pdf):
    exe = shutil.which("pdfinfo")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, str(pdf)], capture_output=True, text=True, timeout=30).stdout
        for line in out.splitlines():
            if line.startswith("Pages:"):
                return int(line.split()[1])
    except Exception:
        pass
    return None


def convert_one(soffice, src, dst, profile, timeout):
    """Convert src to dst atomically. Returns (ok, message)."""
    with tempfile.TemporaryDirectory(prefix="pdfconv_") as tmp:
        cmd = [
            soffice, "--headless", "--norestore", "--nolockcheck",
            f"-env:UserInstallation=file://{Path(profile).as_posix()}",
            "--convert-to", "pdf", "--outdir", tmp, str(src),
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, f"timed out after {timeout}s"
        produced = Path(tmp) / (src.stem + ".pdf")
        if not produced.exists() or produced.stat().st_size == 0:
            return False, (r.stderr or r.stdout or "no PDF produced").strip().splitlines()[-1][:200]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(produced), str(dst))
    return True, ""


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Convert .docx/.pptx to PDF with LibreOffice.")
    ap.add_argument("paths", nargs="*", help="folders or files to convert (default: the course root)")
    ap.add_argument("--root", help="course root (default: parent of the tools folder holding this script)")
    ap.add_argument("--outdir", help="write PDFs here, mirroring the folder structure (default: next to each source)")
    ap.add_argument("--only", choices=["docx", "pptx"], help="convert only one type")
    ap.add_argument("--force", action="store_true", help="rebuild even if the PDF is up to date")
    ap.add_argument("--include-skip", action="store_true", help="also convert files/folders with 'skip' in the name")
    ap.add_argument("--dry-run", action="store_true", help="list what would be converted and exit")
    ap.add_argument("--timeout", type=int, default=900, help="seconds allowed per file (default 900)")
    ap.add_argument("--soffice", help="path to soffice if it is not on PATH")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else here.parent
    targets = [Path(p).resolve() if Path(p).is_absolute() else (Path.cwd() / p).resolve() for p in a.paths] or [root]
    outdir = Path(a.outdir).expanduser().resolve() if a.outdir else None

    jobs = []
    for t in targets:
        if t.is_file():
            if t.suffix.lower() in EXTS:
                jobs.append(t)
        elif t.is_dir():
            jobs += collect(t, a.only, a.include_skip)
        else:
            print(f"! not found: {t}", file=sys.stderr)
    jobs = sorted(set(jobs))

    def dest(src):
        if outdir:
            try:
                return outdir / src.relative_to(root).with_suffix(".pdf")
            except ValueError:
                return outdir / src.with_suffix(".pdf").name
        return src.with_suffix(".pdf")

    todo, uptodate = [], []
    for s in jobs:
        d = dest(s)
        (uptodate if (d.exists() and d.stat().st_mtime >= s.stat().st_mtime and not a.force) else todo).append(s)

    print(f"Root: {root}")
    print(f"Found {len(jobs)} file(s): {len(todo)} to convert, {len(uptodate)} already up to date.")
    if a.dry_run:
        for s in todo:
            print("  would convert:", s.relative_to(root) if root in s.parents else s)
        return 0
    if not todo:
        return 0

    soffice = find_soffice(a.soffice)
    if not soffice:
        print("LibreOffice not found. Install it (see the top of this script) or pass --soffice PATH.", file=sys.stderr)
        return 2

    ok_n, failed = 0, []
    with tempfile.TemporaryDirectory(prefix="lo_profile_") as profile:
        for i, s in enumerate(todo, 1):
            label = s.relative_to(root) if root in s.parents else s
            t0 = time.time()
            ok, msg = convert_one(soffice, s, dest(s), profile, a.timeout)
            if ok:
                ok_n += 1
                pg = pdf_pages(dest(s))
                size = dest(s).stat().st_size / 1e6
                print(f"[{i}/{len(todo)}] OK   {label}  ->  {pg if pg else '?'} pages, {size:.1f} MB, {time.time()-t0:.0f}s")
            else:
                failed.append((label, msg))
                print(f"[{i}/{len(todo)}] FAIL {label}: {msg}")

    print(f"\nDone: {ok_n} converted, {len(uptodate)} skipped (up to date), {len(failed)} failed.")
    for label, msg in failed:
        print(f"  FAILED: {label} - {msg}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
