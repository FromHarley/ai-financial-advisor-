# Contributing

Thanks for your interest in Buffett AI. This document covers the workflow for contributing to the project.

---

## Branch workflow

### Don't commit directly to `main`

`main` is protected. All changes go through a Pull Request with at least one approval.

### Typical workflow

```bash
# Pull latest main
git checkout main
git pull

# Create or switch to your feature branch
git checkout -b your-feature

# Work, commit often with a descriptive prefix
git add .
git commit -m "layer1: add feature importance calculation"

# Push and open a PR
git push origin your-feature
```

---

## Commit messages

Prefix every commit with a tag:

- `layer1:` — ML model
- `layer2:` — GenAI / Claude
- `layer3:` — Agentic / ETF agent
- `layer4:` — Responsible AI
- `app:` — Streamlit UI or shared infrastructure
- `docs:` — Documentation

**Good:** `layer2: add guardrail to check for hallucinated tickers`
**Bad:** `update` or `fix bug`

---

## Pull Request guidelines

Before opening a PR:

1. Your feature works locally
2. You've tested it manually
3. You've added comments where the code is non-obvious

**PR title format:** `layer1: train classifier with cross-validation`

**PR description:** What you changed, how you tested it, anything the reviewer should watch for.

---

## Code style

- **Python 3.11** — don't use 3.12+ features
- **Type hints** on public functions
- **Docstrings** on public functions (one line minimum)
- **No print statements** in production code — use `st.write()` or a logger
- **Never commit API keys**

---

## Secrets policy

- `.env` is gitignored — keep it that way
- If you accidentally commit a key, rotate it immediately

---

## Running locally

```bash
source .venv/bin/activate
streamlit run app.py
```
