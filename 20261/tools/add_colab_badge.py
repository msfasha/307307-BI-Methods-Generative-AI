#!/usr/bin/env python3
"""
add_colab_badge.py - put an "Open in Colab" badge at the top of Jupyter notebooks.

The badge links to  https://colab.research.google.com/github/<user>/<repo>/blob/<branch>/<path>,
so Colab opens the notebook straight from your GitHub repo. It only works once
the notebook has been pushed to that repo at that same path.

What it does for each notebook:
  * no Colab badge yet  -> inserts a small markdown cell at the very top
  * badge already there -> updates its link if the path/repo changed (otherwise leaves it)
  * everything else in the file is kept as it was, and the file's original JSON
    formatting (indent, \\u escapes, trailing newline) is preserved, so a git diff
    shows only the badge cell.

The repo, branch and in-repo path are worked out automatically when the notebook
sits inside a git clone (origin remote + relative path). Otherwise pass
--repo user/repo and --repo-root <folder that corresponds to the repo's top level>.

Usage:
  python3 tools/add_colab_badge.py                       # every *.ipynb under the repo
  python3 tools/add_colab_badge.py "Module 3 - Memory"   # one folder
  python3 tools/add_colab_badge.py path/to/lab.ipynb     # one notebook
  python3 tools/add_colab_badge.py --dry-run             # show links, change nothing
  python3 tools/add_colab_badge.py --only-labs           # only files named *_lab.ipynb
"""
import argparse
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.parse import quote

BADGE_IMG = "https://colab.research.google.com/assets/colab-badge.svg"
COLAB_HREF_RE = re.compile(r'https://colab\.research\.google\.com/github/[^"\s]+')


def git(args, cwd):
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def repo_from_remote(url):
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", url or "")
    return f"{m.group(1)}/{m.group(2)}" if m else None


def badge_source(url):
    return [
        '<div style="display: flex; justify-content: flex-start; align-items: center;">\n',
        f'    <a href="{url}" target="_blank">\n',
        f'        <img src="{BADGE_IMG}" alt="Open In Colab" style="height: 25px;">\n',
        "    </a>\n",
        "</div>",
    ]


def detect_style(raw, nb):
    """Find the json.dumps options that reproduce the file byte-for-byte."""
    for indent in (1, 2, 4):
        for ascii_ in (False, True):
            for sort in (False, True):
                for nl in ("", "\n"):
                    kw = dict(indent=indent, ensure_ascii=ascii_, sort_keys=sort)
                    if (json.dumps(nb, **kw) + nl).encode("utf-8") == raw:
                        return kw, nl
    return None, None


def process(path, url, dry):
    raw = path.read_bytes()
    nb = json.loads(raw)
    kw, nl = detect_style(raw, nb)
    cells = nb.get("cells", [])
    new_nb_note = ""
    # existing badge?
    for c in cells[:5]:
        if c.get("cell_type") == "markdown":
            src = "".join(c.get("source", []))
            if "colab-badge.svg" in src or COLAB_HREF_RE.search(src):
                m = COLAB_HREF_RE.search(src)
                if m and m.group(0) == url:
                    return "already ok", None
                if not m:
                    return "has a badge without a GitHub link - left alone", None
                if not dry:
                    new = src.replace(m.group(0), url)
                    c["source"] = new.splitlines(keepends=True)
                action = "link updated"
                break
    else:
        cell = {"cell_type": "markdown", "metadata": {}, "source": badge_source(url)}
        if any("id" in c for c in cells):  # nbformat 4.5 notebooks that use cell ids
            cell["id"] = uuid.uuid4().hex[:8]
        if not dry:
            cells.insert(0, cell)
        action = "badge added"
    if dry:
        return action + " (dry run)", None
    if kw is None:  # unknown style: fall back to the common Jupyter style
        kw, nl = dict(indent=1, ensure_ascii=False, sort_keys=True), "\n"
        new_nb_note = " (file re-formatted)"
    path.write_text(json.dumps(nb, **kw) + nl, encoding="utf-8")
    return action + new_nb_note, None


def main():
    ap = argparse.ArgumentParser(description="Add/refresh the Open-in-Colab badge in notebooks.")
    ap.add_argument("paths", nargs="*", help="notebooks or folders (default: whole repo / current folder)")
    ap.add_argument("--repo", help="GitHub user/repo (default: from the git origin remote)")
    ap.add_argument("--branch", default=None, help="branch (default: current git branch, else main)")
    ap.add_argument("--repo-root", help="folder that is the repo's top level (default: git top level)")
    ap.add_argument("--only-labs", action="store_true", help="only notebooks whose name ends in _lab.ipynb")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    start = Path(a.paths[0]).resolve() if a.paths else Path.cwd()
    start_dir = start if start.is_dir() else start.parent
    root = Path(a.repo_root).resolve() if a.repo_root else None
    if root is None:
        top = git(["rev-parse", "--show-toplevel"], start_dir)
        root = Path(top) if top else None
    repo = a.repo or (repo_from_remote(git(["remote", "get-url", "origin"], start_dir)) if root else None)
    if not root or not repo:
        print("Could not work out the repo. Pass --repo user/repo and --repo-root <folder>.", file=sys.stderr)
        return 2
    branch = a.branch or (git(["branch", "--show-current"], start_dir) if (root / ".git").exists() else None) or "main"

    targets = [Path(p).resolve() for p in a.paths] or [root]
    files = []
    for t in targets:
        if t.is_file() and t.suffix == ".ipynb":
            files.append(t)
        elif t.is_dir():
            files += [p for p in t.rglob("*.ipynb") if ".ipynb_checkpoints" not in p.parts]
    files = sorted(set(files))
    if a.only_labs:
        files = [f for f in files if f.name.endswith("_lab.ipynb")]

    print(f"Repo: {repo}  branch: {branch}  root: {root}")
    for f in files:
        try:
            rel = f.relative_to(root).as_posix()
        except ValueError:
            print(f"skip (outside repo root): {f}")
            continue
        url = f"https://colab.research.google.com/github/{repo}/blob/{branch}/{quote(rel, safe='/')}"
        status, _ = process(f, url, a.dry_run)
        print(f"  {status:<32} {rel}")
        if a.dry_run:
            print(f"      {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
