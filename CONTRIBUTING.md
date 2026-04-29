# Contributing

This is how the team works on this repo. Read it once before your first commit.

---

## Branch workflow

### Don't commit directly to `main`

`main` is protected. You can't push to it — you have to open a Pull Request and get one approval. This is on purpose: every change gets a second set of eyes, and we always know `main` is working.

### Your branch

Each of us owns one layer, and each layer has one long-lived branch:

- `layer1-ml`
- `layer2-genai`
- `layer3-agentic`
- `layer4-respai`
- `voice-ux`

Work on your branch. When a feature is ready, open a PR to `main`.

### Typical workflow

```bash
# Pull latest main before you start
git checkout main
git pull

# Switch to your branch and bring it up to date
git checkout layer1-ml
git merge main

# Work. Commit often.
git add .
git commit -m "layer1: add feature importance calculation"

# Push your branch
git push origin layer1-ml

# When ready, open a PR on GitHub: layer1-ml → main
```

---

## Commit messages

Prefix every commit with your layer tag:

- `layer1: ...`
- `layer2: ...`
- `layer3: ...`
- `layer4: ...`
- `voice: ...`
- `app: ...` (for changes to `app.py` or shared infra)
- `docs: ...` (README, CONTRIBUTING, model card)

Good examples:

- `layer1: train random forest on financial_risk_profiles.csv`
- `layer2: add guardrail to check for hallucinated tickers`
- `voice: handle empty transcript gracefully`
- `docs: update README with demo day instructions`

Bad examples:

- `update` (what update?)
- `fix bug` (what bug?)
- `wip` (use a branch, not a vague commit)

---

## Pull Request rules

### When to open a PR

- Your feature works on your branch
- You've tested it at least once manually
- You've added comments where the code is non-obvious
- You've updated the README if you changed how something works

### PR title

Same format as commit messages: `layer1: train classifier with cross-validation`

### PR description

Use the template in `.github/pull_request_template.md`. At minimum:

1. What you changed
2. How you tested it
3. Anything the reviewer should pay special attention to

### Review expectations

- **Everyone reviews at least one PR per week.** Even if it's not your layer, you should know what's landing in `main`.
- **One approval required to merge.** Two approvals if the PR touches `app.py` or any other layer's code.
- **Don't rubber-stamp.** Actually open the file, read the change, run the code if you can.
- **Comment kindly.** "This will fail if `etfs` is empty — can you add a guard?" is a good comment. "This is wrong" is not.

### Who should review

- Layer 1 PRs → reviewed by Alex (Layer 4 integrates with Layer 1 closely)
- Layer 2 PRs → reviewed by Alex or Layer 1 owner
- Layer 3 PRs → reviewed by Layer 2 owner (they'll consume its output)
- Layer 4 PRs → reviewed by any teammate
- Voice PRs → reviewed by Alex
- `app.py` changes → reviewed by two teammates (it's the integration point)

---

## Code style

- **Python 3.11.** Don't use 3.12-only features.
- **Type hints on public functions.** `def predict_risk_tier(profile: dict) -> dict:` — yes. `def predict_risk_tier(profile):` — no.
- **Docstrings on public functions.** One line describing what it does. Inputs and outputs.
- **No print statements in production code.** Use `streamlit.write()` for user-facing output or a proper logger for debugging.
- **Never commit API keys, even temporarily.** If you accidentally commit one, tell Alex immediately so we can rotate it.

---

## Secrets policy

- **`.env` is gitignored.** Keep it that way.
- **Don't paste API keys in Discord, Slack, email, or anywhere else.** If you need a key, DM Alex.
- **If you expose a key, tell Alex immediately.** We rotate it, no blame attached. Hiding a leak is the only thing that causes actual problems.

---

## Running the app locally

```bash
source .venv/bin/activate
streamlit run app.py
```

If Streamlit doesn't reload on file changes, add this to your Streamlit config (`~/.streamlit/config.toml`):

```toml
[server]
runOnSave = true
```

---

## Stuck?

1. Check the function signature in your layer's stub — your output has to match the contract.
2. Check the README for setup steps you might have skipped.
3. Ask in the team Discord with the layer name + what error you're seeing.
4. If it's a design question (not a bug), bring it to the next meeting — don't litigate it in chat.

---

## One final note

This project is going on all of our resumes. Treat every commit like you'd want a future employer to read it — because they might.
