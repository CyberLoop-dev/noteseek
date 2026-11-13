#!/usr/bin/env python3
"""noteseek: offline BM25 search over a folder of Markdown / text notes.

    python noteseek.py "oauth refresh token" ~/notes
    python noteseek.py "meeting with sara" ~/notes -n 3 --json
"""
import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
TOKEN = re.compile(r"\w+", re.UNICODE)
HEADING = re.compile(r"^#{1,6}\s+(.*)")
STOP = set("a an and are as at be but by for from has have if in into is it its of on or so that the their then there these this to was were will with".split())
CHUNK_TARGET = 350  # characters before a blank line may close a chunk


def tokens(text):
    return [t for t in (w.lower() for w in TOKEN.findall(text)) if t not in STOP]


def split_file(path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    chunks, heading, buf, start, size = [], "", [], 1, 0

    def flush():
        nonlocal buf, size
        body = "\n".join(buf).strip()
        if body:
            chunks.append({"file": str(path), "line": start, "heading": heading, "text": body})
        buf, size = [], 0

    for n, line in enumerate(text.splitlines(), 1):
        h = HEADING.match(line)
        if h:
            flush()
            heading, start = h.group(1).strip(), n
        if not buf:
            start = n
        if line.strip() == "" and size >= CHUNK_TARGET:
            flush()
            continue
        buf.append(line)
        size += len(line) + 1
    flush()
    return chunks


def collect(root, exts):
    root = Path(root).expanduser()
    if root.is_file():
        files = [root]
    else:
        files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts
                 and not any(part.startswith(".") for part in p.relative_to(root).parts)]
    out = []
    for f in sorted(files):
        out += split_file(f)
    return out


def rank(chunks, query, k1=1.5, b=0.75):
    q = list(dict.fromkeys(tokens(query)))
    if not q or not chunks:
        return [], q
    docs = [tokens(c["heading"] + " " + c["heading"] + " " + c["text"]) for c in chunks]  # heading counts double
    n = len(docs)
    avgdl = sum(len(d) for d in docs) / n or 1
    df = Counter()
    for d in docs:
        df.update(set(d))
    scored = []
    for chunk, d in zip(chunks, docs):
        tf = Counter(d)
        score = 0.0
        for t in q:
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avgdl))
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: -x[0])
    return scored, q


def highlight(text, terms):
    if not USE_COLOR or not terms:
        return text
    pat = re.compile("(" + "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True)) + ")", re.I)
    return pat.sub("\033[1;33m\\1\033[0m", text)


def snippet(text, terms, width=260):
    flat = " ".join(text.split())
    low = flat.lower()
    pos = min((low.find(t) for t in terms if low.find(t) >= 0), default=0)
    a = max(0, pos - width // 4)
    piece = flat[a:a + width]
    return ("…" if a else "") + piece + ("…" if a + width < len(flat) else "")


def main():
    ap = argparse.ArgumentParser(description="BM25 search over your notes, fully offline.")
    ap.add_argument("query")
    ap.add_argument("path", nargs="?", default=".", help="folder or file to search (default: current folder)")
    ap.add_argument("-n", type=int, default=5, help="number of results (default 5)")
    ap.add_argument("--ext", default=".md,.markdown,.txt,.org,.rst", help="comma-separated extensions")
    ap.add_argument("--json", action="store_true", help="print results as JSON (handy for feeding an LLM)")
    a = ap.parse_args()

    exts = {e if e.startswith(".") else "." + e for e in a.ext.lower().split(",") if e}
    chunks = collect(a.path, exts)
    if not chunks:
        sys.exit(f"noteseek: no notes found under {a.path} ({', '.join(sorted(exts))})")
    ranked, terms = rank(chunks, a.query)
    top = ranked[:a.n]

    if a.json:
        print(json.dumps([{"score": round(s, 4), "file": c["file"], "line": c["line"],
                           "heading": c["heading"], "text": c["text"]} for s, c in top],
                         indent=2, ensure_ascii=False))
        return
    if not top:
        print("No matches.")
        return
    for i, (score, c) in enumerate(top, 1):
        loc = f"{c['file']}:{c['line']}"
        head = f"  # {c['heading']}" if c["heading"] else ""
        print(f"\033[1;36m{i}. {loc}\033[0m\033[2m{head}  (score {score:.2f})\033[0m" if USE_COLOR
              else f"{i}. {loc}{head}  (score {score:.2f})")
        print("   " + highlight(snippet(c["text"], terms), terms))
        print()


if __name__ == "__main__":
    main()
