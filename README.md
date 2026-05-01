# AI Financial Advisor

An autonomous financial advisor that profiles investor risk tolerance, recommends an ETF portfolio, and explains its reasoning in plain English — with a conversational voice interface and a human approval step before any recommendation is finalized.

**Course:** MIS 02.303 — AI in Business, Spring 2026
**Instructor:** Prof. Hema Kadali
**Team:** Alexander Harley (Project Lead), Daniel Duffy, Anurag Pratapbhai Luhar, Kimberly Ting
**Due:** Tuesday, May 5, 2026

---

## What this project is

This is a working end-to-end AI system with four integrated layers, deployed to a public URL accessible from any device:

1. **Machine Learning (Layer 1)** — A trained classifier predicts risk tier (Low/Medium/High) from the user's financial profile. SHAP explains which features drove the prediction.
2. **Generative AI (Layer 2)** — Claude (Anthropic API) writes a plain-English explanation of the recommendation for a non-technical user.
3. **Agentic AI (Layer 3)** — An agent fetches live market data via `yfinance` and selects an ETF shortlist matching the user's risk tier.
4. **Responsible AI (Layer 4)** — SHAP plots are visible in the UI, a bias audit is documented in the model card, and no decision is logged without explicit user approval.

The app is deployed to **Streamlit Community Cloud** so Prof. Kadali can access it from a phone or laptop browser via a shared URL.

> **Stretch goal (not committed):** A conversational voice interface (speech-to-text input, text-to-speech output) is scaffolded in `voice_ux/` for possible deployment if the team finishes ahead of schedule. The voice layer is documented in our Future Directions slide as the next iteration of the system.

---

## Team roles

Roles assigned at the kickoff meeting on **04-20**.

| Layer | Owner | Branch | What they'll do |
|---|---|---|---|
| Layer 1 — ML + SHAP | Alex Harley | `layer1-ml` | Train a classifier on `financial_risk_profiles.csv`, produce SHAP visualizations, write the metrics section of the model card. |
| Layer 2 — GenAI (Claude) | Anurag Luhar | `layer2-genai` | Design the Claude prompt that turns tier + SHAP + ETFs into a 2–3 sentence explanation. Enforce guardrails. |
| Layer 3 — Agentic | Kimberly Ting | `layer3-agentic` | Build the tier→ETF mapping and the yfinance fetch. Make it robust enough to demo on stage. |
| Layer 4 — Responsible AI | Daniel Duffy | `layer4-respai` | Bias audit, model card, decision logging, integration merge on 04-30, and Streamlit Cloud deployment. |
| Voice / UX | **Out of scope** (deferred) | `voice-ux` | Stretch goal only — Alex may explore independently if Layer 1 finishes ahead of schedule. Documented in Future Directions slide. |

**Project Lead responsibilities (Alex, in addition to Layer 1):**
- Holds the overall schedule and unblocks teammates
- Owns the integration merge on 04-30
- Deploys the final app to Streamlit Community Cloud
- Submits to Canvas by 6 PM on 05-05

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow each owner follows.

---

## Project structure

```
ai-financial-advisor/
├── app.py                   # Streamlit entry point — the full UI lives here
├── requirements.txt         # Pinned dependencies (Python 3.11)
├── .env.example             # Template for API keys (copy to .env)
├── .gitignore
├── README.md
├── CONTRIBUTING.md
├── data/
│   ├── financial_risk_profiles.csv   # ML training data (2,000 rows)
│   └── cfpb_financial_wellbeing.csv  # Bias audit data (2,000 rows)
├── layer1_ml/
│   ├── __init__.py
│   ├── train.py             # Offline: trains RandomForest, saves model.pkl
│   ├── predict.py           # Runtime: predict_risk_tier(profile) → dict
│   └── model.pkl            # Gitignored — produced by train.py
├── layer2_genai/
│   ├── __init__.py
│   ├── claude_client.py     # generate_explanation(...) → str
│   └── prompts.py           # System + user prompt templates
├── layer3_agentic/
│   ├── __init__.py
│   ├── etf_agent.py         # get_etf_recommendations(tier) → list[dict]
│   └── tier_mapping.py      # Hard-coded tier → ETF rules
├── layer4_respai/
│   ├── __init__.py
│   ├── bias_audit.py        # Produces the audit chart + finding
│   ├── model_card.md        # Final deliverable document
│   └── decision_log.py      # log_decision(...) — writes to decisions.csv
├── voice_ux/
│   ├── __init__.py
│   ├── transcribe.py        # transcribe_profile(audio) → dict
│   ├── speak.py             # speak(text) — browser SpeechSynthesis
│   └── parser.py            # Extracts structured fields from transcript
└── .github/
    └── pull_request_template.md
```

---

## Setup (first time)

**Requires Python 3.11.** Check with `python --version` — if you have 3.10 or older, upgrade before starting.

### 1. Clone the repo

```bash
git clone https://github.com/[ORG]/ai-financial-advisor.git
cd ai-financial-advisor
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# or
.venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API keys

Copy the template:

```bash
cp .env.example .env
```

Then open `.env` and fill in:

- **`ANTHROPIC_API_KEY`** — Ask Alex directly (DM, not group chat). We are using one shared key for this project. Do not post this key anywhere.
- **`OPENAI_API_KEY`** — Only required if you're working on the voice feature (used for Whisper transcription). If you're only touching Layers 1/2/3/4, you can leave this blank.

**Never commit `.env`.** It's in `.gitignore` and must stay there.

### 5. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Running without voice (fallback mode)

Voice is optional — the app works without it. If you don't want to set up the OpenAI key or your microphone isn't cooperating, click the **"Use keyboard input"** toggle in the sidebar. You'll get a normal form instead of the microphone button. Everything else (ML, GenAI, agent, bias audit) works identically.

**On demo day, keyboard is our backup.** If voice breaks on stage, we switch to keyboard without narrating the failure.

---

## What each layer owner needs to do

Every layer has a stub function with the correct signature and a `NotImplementedError`. Open your layer's folder, find your stub, and replace the body. The function signatures are contracts — don't change the inputs or outputs without discussing at a meeting.

- **Layer 1 (ML):** Open `layer1_ml/train.py` first. Run it once to produce `model.pkl`. Then fill in `layer1_ml/predict.py`. Build training in a Colab notebook for clarity, then export to a script.
- **Layer 2 (GenAI):** Open `layer2_genai/prompts.py` to design your prompt, then `layer2_genai/claude_client.py` to wire the API call.
- **Layer 3 (Agentic):** Open `layer3_agentic/tier_mapping.py` (decide which ETFs go with which tier), then `layer3_agentic/etf_agent.py` (yfinance calls).
- **Layer 4 (Responsible AI):** `layer4_respai/bias_audit.py` generates the chart and writes findings to the model card. Also owns `decision_log.py`. Owns Streamlit Cloud deployment after integration.

---

## Deliverables checklist

- [ ] `app.py` — end-to-end demo runs in under 45 seconds
- [ ] `layer1_ml/model.pkl` — trained, with metrics documented
- [ ] `layer1_ml/training_notebook.ipynb` — accuracy, precision/recall, confusion matrix, SHAP
- [ ] `layer4_respai/model_card.md` — 1-2 pages, complete
- [ ] `layer4_respai/bias_audit_chart.png` — produced by `bias_audit.py`
- [ ] **Deployed to Streamlit Community Cloud** — public URL accessible from any device
- [ ] Presentation slides — 10 minutes, includes Future Directions slide
- [ ] This README — reviewed and current

## Deployment

The app is deployed to **Streamlit Community Cloud** (free tier).

To deploy or redeploy:

1. Sign in at [share.streamlit.io](https://share.streamlit.io) with your GitHub account
2. Click **New app** → select this repo → set main file to `app.py`
3. Add API keys under **Advanced settings → Secrets**:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Click **Deploy** — app is live at a public URL in 2-3 minutes

Owner: Alex (Project Lead). Deployment happens after integration on 04-30 and is locked in by the dress rehearsal on 05-05 6pm.

---

## Timeline

See the full [blueprint doc](../Autonomous_Financial_Advisor_Team_Blueprint_v2.docx) for dates. Key checkpoints:

- **Thu 04-30** — Integration day
- **Mon 05-04** — Testing, full end-to-end demo
- **Tue 05-05** — Dress rehearsal

---

## Getting help

- Technical blocker on your layer? Post in the Discord with the branch name and what you tried.
- Blueprint question? Bring it to the 04-21 in-class working session with Prof. Kadali.
- API key issue? DM Alex directly.

---

*Built with Claude Opus 4.7 as a development assistant. All design choices, code review, and final deliverables are the team's own work per the course AI-use policy.*
