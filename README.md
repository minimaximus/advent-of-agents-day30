# Advent of Agents S3: Day 30 — No More Spooky Results: Continuous Alignment with Golden Evals & AQuA 🎃🍬

An ADK agent (`candy_auditor`) audits neighborhood Trick-or-Treat houses (`HOUSE-1031`, `HOUSE-666`, `HOUSE-404`) using modular skills (`SkillToolset`) and lookup tools, generating an **Official Trick-or-Treat House Audit Memorandum**.

This **Layer 5 (Regression Testing & Continuous Alignment)** Kata answers the two questions every team faces when shipping AI agents to production:
1. **Pre-Deploy Regression Testing (Shift-Left)**: *"How do we verify that updated models or system prompts comply with our established policies before shipping updates?"* → Run automated **Golden-Dataset Policy Evaluation Pipelines** for **Gemini Agent** (`make kata` / `make eval`, `make explain`, `make fix`).
2. **Post-Deploy Continuous Alignment (Shift-Right)**: *"Your agent served 1,240 conversations yesterday. How do we verify that the agent adhered to all compliance and rules in production?"* → Run **AQuA (Ambient Quality Agent)** (`make aqua`, [`eval_harness/run_aqua.py`](eval_harness/run_aqua.py)) against recorded production transcripts ([`eval_harness/prod_sessions.json`](eval_harness/prod_sessions.json)) to review sampled sessions against a **9-question compliance checklist**, verify clusters against real transcripts, diagnose root causes in [`candy_auditor/agent.py`](candy_auditor/agent.py), and track **14-day regression resolution**.

---

## Core Concepts

- **The Vibe-Check Trap**: When a model or prompt update makes an agent "more concise," tone and formatting metrics (`spooky-vibe: 5.0/5.0`) stay green and no Python errors are logged—even when the agent silently drops a mandatory pricing formula or allergen cross-contact warning.
- **Golden-Dataset Policy Pipeline (`EvalTask` & `PointwiseMetricPromptTemplate`)**: A curated benchmark of edge-case houses (`HOUSE-1031`, `HOUSE-666`, `HOUSE-404`) graded on explicit 1–5 policy rubrics (`cost-per-treat`, `neighboring-allergen-risk`). Returns both a **numeric score (`1–5`)** and an actionable **Gemini Judge Rationale** explaining any compliance breach.
- **AQuA (Ambient Quality Agent)**: A second deployment in your Google Cloud project that runs beside your ADK agent (daily and 15 minutes after every deploy). It reads session telemetry + the deployed source snapshot in GCS and writes verified insights to its own BigQuery dataset.
- **The 9-Question Session Compliance Checklist**: For each sampled production session (up to 1,000/run), AQuA checks compliance against the agent's own instructions and tools across 9 dimensions: *Procedure, Output requirements, Tool selection, Tool arguments, Tool results, Progress & completion, Grounding, Answer quality,* and *Configuration*.
- **Cluster, Verify & Code-Anchored RCA**: AQuA clusters raw findings by root cause, re-checks up to 3 full transcripts per cluster to automatically drop false positives, points to the exact line of code/instructions causing the bug, and tracks a **14-day resolution clock** (`OPEN` → `RESOLVED` after 14 clean days).

---

## Pre-Deploy Policy Rubrics (`eval_harness/rubrics.json`)

| Criterion ID | Policy / Compliance Rule | Role in Pre-Deploy Gate |
| :--- | :--- | :--- |
| `spooky-vibe` | Festive Halloween tone (shows why vibe checks miss policy bugs!) | `Vibe Check (Tone)` — Diagnostic only (`5.00 / 5.0`) |
| `candy-tier-breakdown` | Explicit House ID, size class, wrapper status, Guild tier, trade ratio | `Format Policy` — Diagnostic (`5.00 / 5.0`) |
| `cost-per-treat` | Exact `$/treat` and `$/oz` division math + `$0.50` Golden Pumpkin benchmark | **Pricing Policy Gate (`Mean >= 4.0`)** — Regressed: `1.33` → Fixed: `5.00 ✅` |
| `neighboring-allergen-risk` | Audits `neighboring_bowls` on porch for unwrapped peanut/tree-nut cross-contact | **Safety Policy Gate (`Mean >= 4.0`)** — Regressed: `1.00` → Fixed: `5.00 ✅` |

---

## The 5-Minute Kata Walkthrough

Full step-by-step instructions can be found in [`docs/LAB.md`](docs/LAB.md).

```bash
# 1. Act I (Pre-Deploy Gate): Catch a policy regression before shipping (fails at 1.33 & 1.00)
make kata          # (or `make eval` for live cloud grading)

# 2. Act I (Diagnose): Read the Gemini Judge's exact compliance breach rationales
make explain

# 3. Act II (Align & Re-Verify): Restore policy compliance in SKILL.md and pass the Golden Gate (5.00/5.0)
make fix
make kata

# 4. Act III (Post-Deploy Continuous Alignment): Run AQuA across 1,240 Halloween production sessions
make aqua
```

---

## Project Layout

```text
candy_auditor/              ADK Agent (`agent.py`), tools (`bowl_tool.py`, `preference_tool.py`), and `skills/`
tools_data/                 Halloween porch dataset (`houses.json`) and Guild trade index (`trade_values.json`)
eval_harness/               Gemini Agent Golden-Dataset Gate (`run_hillclimb.py`), Judge rationales (`explain_criteria_results.py`), and AQuA runner (`run_aqua.py`)
docs/LAB.md                 Step-by-step walkthrough of Pre-Deploy Golden Evals + Post-Deploy AQuA
```

---

## Resources

- [AQuA: An Ambient Quality Agent That Diagnoses Your Production Agent](https://g.dev/cloud/adventofagents-season3-blog-aqua-ambient-quality-agent)
- [Gemini Platform Evaluation Service](https://g.dev/cloud/adventofagents-season3-docs-genai-evaluation-overview)
- [ADK Documentation and SkillToolset Guide](https://g.dev/cloud/adventofagents-season3-docs-adk)
- [Agent Starter Pack Templates](https://g.dev/cloud/adventofagents-season3-agent-starter-pack)

