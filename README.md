<div align="center">

<img src="assets/banner.svg" alt="noteseek" width="100%">

<p>
  <img alt="License" src="https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge">
  <img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-fbbf24?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Dependencies" src="https://img.shields.io/badge/dependencies-zero-fb7185?style=for-the-badge">
</p>

**Find the paragraph you wrote six months ago. No cloud, no API keys, no embeddings.**

</div>

---

## ✨ Features

- 🔎 **BM25 ranking**, the same family of scoring used by classic search engines
- 🧩 Splits notes into **small chunks** (by heading and paragraph) so you get the exact passage, not just the file
- 🎯 Shows `file:line`, the heading it sits under, and a snippet with your terms highlighted
- 🌍 Unicode-aware: works with English, Persian, and any language split by spaces
- 🧠 `--json` output you can paste into an LLM prompt as context
- 🪶 One file, pure standard library

## 🚀 Usage

```bash
git clone https://github.com/CyberLoop-dev/noteseek.git
cd noteseek

python3 noteseek.py "oauth refresh token" ~/notes
python3 noteseek.py "meeting with sara" ~/notes -n 3
python3 noteseek.py "docker volumes" ~/notes --json
```

Example:

```text
1. /home/alex/notes/dev/auth.md:42  # Refresh tokens  (score 7.31)
   ...store the refresh token server-side and rotate it on every use...

2. /home/alex/notes/inbox.md:8  # Todo  (score 3.90)
   ...look into how the refresh token flow works with the mobile app...
```

| Flag | Meaning |
|---|---|
| `-n N` | Number of results (default 5) |
| `--ext .md,.txt` | Which file extensions to read |
| `--json` | Machine-readable output |

Hidden folders (like `.git`) are skipped.

## 🧠 Using it with an LLM

This is the *retrieval* half of a RAG workflow. Pipe the top passages into whatever model you use:

```bash
python3 noteseek.py "what did I decide about pricing" ~/notes -n 4 --json
```

## ⚖️ Honest limits

It matches **words**, not meaning: a note about "automobile" will not be found by "car". That is the trade-off for being instant, offline and dependency-free. The index is rebuilt on every run, which is fine for personal note collections.

## 📄 License

MIT
