# 👋 Start Here

If you're new to this repo, read this file first. It takes 5 minutes and saves you an hour.

This is the AI Financial Advisor project for **MIS 02.303 Group 2**. Below is everything you need to find your way around.

---

## 1. What you're looking at

This repo contains a working AI app with **four AI layers**:

- **Layer 1 — Machine Learning** (predicts a user's risk tier)
- **Layer 2 — Generative AI** (Claude writes a plain-English explanation)
- **Layer 3 — Agentic AI** (an agent picks ETFs and pulls live prices)
- **Layer 4 — Responsible AI** (bias audit, model card, human approval gate)

Each teammate owns one layer. The four layers come together in `app.py`, which is the actual app the user sees.

---

## 2. Where to look first

Read in this order:

1. **`README.md`** — Big-picture project overview, deliverables checklist, deployment instructions. Read this fully.
2. **`CONTRIBUTING.md`** — How we work together. Branch rules, commit format, PR process, secrets handling. Don't skip this.
3. **Your layer's folder** — Whichever one you own. Each folder has 2-3 Python files with clear `TODO` markers showing what to build.

That's it. You don't need to read other layers' folders unless you're curious or reviewing a teammate's PR.

---

## 3. The folder map (one sentence each)

```
ai-financial-advisor/
├── app.py                  ← The Streamlit app. Don't edit unless you're integrating.
├── README.md               ← Read this first.
├── CONTRIBUTING.md         ← How we work as a team.
├── START_HERE.md           ← This file.
├── requirements.txt        ← Python packages. Run `pip install -r requirements.txt`.
├── .env.example            ← Template. Copy to `.env` and add your API key.
├── .gitignore              ← Files git ignores (including .env — never commit secrets).
│
├── data/                   ← The two CSVs we use. Don't modify these.
│
├── layer1_ml/              ← Daniel's folder — ML model training & prediction.
├── layer2_genai/           ← Anurag's folder — Claude API + prompts.
├── layer3_agentic/         ← Kimberly's folder — ETF agent + yfinance.
├── layer4_respai/          ← Alex's folder — bias audit, model card, decision log.
└── voice_ux/               ← Deferred (out of scope). Stretch goal only.
```

---

## 4. The five-minute setup

You only do this once on your machine.

```bash
# 1. Clone the repo (you may have already done this)
git clone https://github.com/FromHarley/ai-financial-advisor-.git
cd ai-financial-advisor-

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
# OR
.venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API keys
cp .env.example .env
# Open .env in a text editor, paste in the API key Alex sent you privately.
# DO NOT post the key in any group chat.

# 5. Run the app to see what it looks like
streamlit run app.py
```

If `streamlit run app.py` opens a browser tab with the app, you're set. The app will show stub responses (fake data) until each layer is filled in — that's expected.

---

## 5. The branch you work on

Each layer has its own branch. **Never work directly on `main`.**

```bash
# Switch to your assigned branch
git checkout layer1-ml      # 
git checkout layer2-genai   # 
git checkout layer3-agentic # 
git checkout layer4-respai  # 
```

When in doubt, run `git status` to see which branch you're on. The first line tells you.

---

## 6. The flow when you have working code

```bash
# Save your work
git add .
git status                                    # Check what you're committing — make sure .env is NOT in this list
git commit -m "layer1: short description"     # Use your layer prefix
git push origin layer1-ml                      # Replace with your branch

# When ready to merge into main:
# 1. Go to github.com → your repo → Pull Requests → New Pull Request
# 2. Set base: main, compare: your-branch
# 3. Tag a teammate for review
# 4. Once they approve, merge
```

Full details are in `CONTRIBUTING.md`.

---

## 7. The three rules that matter most

1. **Work on your branch, never on `main`.** Open a PR to merge. Always.
2. **Never commit `.env` or any API keys.** If you do by accident, tell Alex *immediately* — fixable if caught fast.
3. **Don't change function signatures without telling the team.** The contracts between layers (inputs/outputs of each function) are locked. Change them and you break someone else's code.

---

## 8. When you get stuck

In order:

1. **Re-read your layer's stub file.** It has a `TODO` comment that explains exactly what to build.
2. **Check the README's "What each layer owner needs to do" section.**
3. **Post in the team Discord** with the error message, branch name, and what you tried.
4. **Bring it to the next team meeting** if it's a design question, not a bug.

---

## 9. Important dates

| Date | What's due |
|---|---|
| **04-30 (Thu)** | Integration day — full app runs end-to-end |
| **05-03 (Sun)** | Presentation slides drafted |
| **05-04 (Mon)** | Dress rehearsal + Streamlit Cloud deployment locked in |
| **05-05 (Tue)** | Final submission to Canvas, midnight deadline |

Full timeline is in the team blueprint document.

---

## 10. Who owns what

| Layer | Owner | GitHub Handle |
|---|---|---|
| Layer 1 — ML |  | `[handle]` |
| Layer 2 — GenAI |  | `[handle]` |
| Layer 3 — Agentic |  | `[handle]` |
| Layer 4 — Responsible AI |  | `[handle]` |

If you need API keys, deployment access, or have a question that affects multiple layers — DM Alex.

---

**Welcome to the project. Read your layer's folder, set up your environment, and let's build something we're proud of.**
