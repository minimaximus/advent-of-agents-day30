# The Lab: Continuous Alignment with Golden-Dataset Policy Evals & AQuA 🎃🌊

This walkthrough takes under five minutes. You will verify **Layer 5: Continuous Alignment** across both pre-deploy and post-deploy stages:
1. **Pre-Deploy Regression Testing (Shift-Left)**: Run an automated **Golden-Dataset Policy Pipeline** in GEAP to catch a prompt regression where the agent passes the vibe check (`5.00/5.0`) while violating pricing and allergen safety policies (`1.33` & `1.00`), inspect the Gemini Judge's rationales, and restore policy compliance in `SKILL.md`.
2. **Post-Deploy Continuous Alignment (Shift-Right)**: Run **AQuA (Ambient Quality Agent)** (`make aqua`, [`eval_harness/run_aqua.py`](../eval_harness/run_aqua.py)) on recorded Halloween production transcripts ([`eval_harness/prod_sessions.json`](../eval_harness/prod_sessions.json)) to see how AQuA's **9-question compliance checklist**, **transcript verifier**, **code-anchored root cause analysis**, and **14-day resolution clock** catch silent compliance failures that never appear in error logs.

---

## The Setup

The Neighborhood Trick-or-Treat Guild runs **`candy_auditor`** ([`candy_auditor/agent.py`](../candy_auditor/agent.py)), an ADK agent equipped with three skills in its `SkillToolset`:
- [`analyze-porch-tier`](../candy_auditor/skills/analyze-porch-tier/SKILL.md)
- [`analyze-candy-value`](../candy_auditor/skills/analyze-candy-value/SKILL.md)
- [`analyze-allergen-safety`](../candy_auditor/skills/analyze-allergen-safety/SKILL.md)

When given a House ID (`HOUSE-1031`, `HOUSE-666`, `HOUSE-404`), the agent calls `get_porch_candy_data` and `get_kid_trade_index` to inspect the porch's candy offering and write a structured audit memorandum.

---

## Step 1: Run the Pre-Deploy Golden-Dataset Policy Gate (`make kata` / `make eval`)

Suppose someone updated the agent's skills to make reports "faster and more conversational" before Halloween night. Run the Golden-Dataset Policy Gate across the 3 benchmark houses:

```bash
make kata     # (or `make eval` for live cloud execution)
```

Output:
```text
criterion_id                 policy_role               mean    min     required     result
--------------------------------------------------------------------------------------
spooky-vibe                  Vibe Check (Tone)         5.00    5.0   diagnostic   ℹ️  info
candy-tier-breakdown         Format Policy             5.00    5.0   diagnostic   ℹ️  info
cost-per-treat               Pricing Policy Gate       1.33    1.0    mean>=4.0     ❌ FAIL
neighboring-allergen-risk    Safety Policy Gate        1.00    1.0    mean>=4.0     ❌ FAIL
--------------------------------------------------------------------------------------

❌ POLICY GATE FAILED (2 regression breach(es) below 4.0 target)
```

Notice why a casual spot-check would have failed us: `spooky-vibe` is a perfect `5.00`, yet the agent violated both mandatory Guild policies.

---

## Step 2: Diagnose the Compliance Breach with Judge Rationales (`make explain`)

Inspect the explanations returned by the GEAP Gemini Judge for any house scoring `<= 4.0`:

```bash
make explain
```

The rationales pinpoint the exact policy breaches:
- **`cost-per-treat`**: *"The response states the raw homeowner spend ($36.00) and piece count (40 treats, 80.0 oz), which are the components needed for the calculation, but it completely omits the mathematical Cost-Per-Treat ($0.90/treat) and Cost-Per-Ounce ($0.45/oz) derivations."*
- **`neighboring-allergen-risk`**: *"The response only evaluates `main_bowl_allergens` (milk, soy, egg_whites) and falsely declares `HOUSE-1031` Peanut-Safe. It completely ignores `neighboring_bowls`, missing the unwrapped 'Homemade Unwrapped Peanut Butter Fudge & Crushed Walnut Brittle' located 4 inches from the main cauldron."*

---

## Step 3: Restore Policy Compliance & Re-Run the Gate (`make fix` & `make kata`)

Apply the policy compliance fixes to [`analyze-candy-value/SKILL.md`](../candy_auditor/skills/analyze-candy-value/SKILL.md) and [`analyze-allergen-safety/SKILL.md`](../candy_auditor/skills/analyze-allergen-safety/SKILL.md):

```bash
make fix
```

Now re-run the Golden-Dataset Policy Gate:

```bash
make kata     # (or `make eval`)
```

```text
criterion_id                 policy_role               mean    min     required     result
--------------------------------------------------------------------------------------
spooky-vibe                  Vibe Check (Tone)         5.00    5.0   diagnostic   ℹ️  info
candy-tier-breakdown         Format Policy             5.00    5.0   diagnostic   ℹ️  info
cost-per-treat               Pricing Policy Gate       5.00    5.0    mean>=4.0     ✅ PASS
neighboring-allergen-risk    Safety Policy Gate        5.00    5.0    mean>=4.0     ✅ PASS
--------------------------------------------------------------------------------------

🎃 GOLDEN DATASET GATE PASSED! All policy compliance criteria achieved Mean Score >= 4.0 / 5.0!
```

---

## Step 4: Post-Deploy Continuous Alignment with AQuA (`make aqua`)

Golden datasets test the benchmark cases you thought of *before* shipping. What happens *after* you deploy and serve 1,240 live Trick-or-Treat sessions?

Run the AQuA post-deploy continuous alignment report:

```bash
make aqua
```

Inspect the 4 stages of AQuA's output:
1. **One Run Funnel (`1,240 sessions -> 3 verified insights`)**: Uniformly samples up to `1,000` sessions per run and reviews each against the agent's own instructions and tools.
2. **The 9-Question Session Compliance Checklist**:
   - `04 Tool arguments` fires on **38 sessions** where the model invented `guild_tier="Ultra-King"` (which raises `ValueError` in error logs).
   - `07 Grounding` fires on **22 sessions** where the agent declared a porch *"Certified Peanut-Safe"* **without calling `get_porch_candy_data` at all** (which leaves **zero errors** in Cloud Logging!).
3. **Cluster, Verify & Triage**: Groups 74 findings into 4 root-cause clusters and re-checks 3 full transcripts per cluster—automatically dropping a 9-session false-positive cluster.
4. **Code-Anchored Diagnosis & 14-Day Resolution Clock**: Reads the evidence conversations + the deployed GCS source snapshot (`candy_auditor/agent.py`), suggests a line-level fix without auto-applying it, and tracks the insight across daily and post-deploy runs until **14 consecutive clean days** mark it `RESOLVED`.
