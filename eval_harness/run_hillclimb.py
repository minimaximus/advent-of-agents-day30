"""Hill-Climbing Evaluation & Build Gate Runner (`make eval` / `make hillclimb`).

Runs the `candy_auditor` ADK agent across the target Halloween houses, grades the reports
using Gemini platform Pointwise Rubric Autoraters, prints a unified Build Gate Scorecard table
(comparing Fluff/Trap criteria vs. Reliable Target criteria), and enforces Mean >= 4.0.
"""

import argparse
import json
import math
import os
import re
import statistics
import sys

from eval_harness.create_candy_evalset import build_candy_evalset
from eval_harness.run_gemini_eval import GeminiEvalRunner


def get_next_run_dir(runs_dir: str, base_name: str = "hillclimb") -> str:
    if not os.path.exists(runs_dir):
        os.makedirs(runs_dir, exist_ok=True)
        return os.path.join(runs_dir, f"{base_name}_1")
    max_idx = 0
    for d in os.listdir(runs_dir):
        m = re.match(rf"^{re.escape(base_name)}_(\d+)$", d)
        if m:
            max_idx = max(max_idx, int(m.group(1)))
    return os.path.join(runs_dir, f"{base_name}_{max_idx + 1}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Halloween Candy Bowl Auditor Hill-Climbing & Gemini platform Gate."
    )
    parser.add_argument("--houses-file", default="eval_harness/hillclimb_houses.txt")
    parser.add_argument("--rubrics-file", default="eval_harness/rubrics.json")
    parser.add_argument("--agent-dir", default="candy_auditor")
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--target-threshold", type=float, default=4.0)
    parser.add_argument("--fast", action="store_true", help="Run fast local synthesis + rubric grading")
    args = parser.parse_args()

    with open(args.houses_file, "r", encoding="utf-8") as f:
        house_ids = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

    runs_dir = os.path.abspath(args.runs_dir)
    run_dir = get_next_run_dir(runs_dir, "hillclimb")
    os.makedirs(run_dir, exist_ok=True)
    run_name = os.path.basename(run_dir)

    evalset_path = os.path.abspath(os.path.join(args.agent_dir, f"{run_name}.evalset.json"))

    print(f"\n🎃 [1/2] Generating ADK Agent Traces ({run_name}) for {house_ids}...")
    build_candy_evalset(
        house_ids=house_ids,
        output_path=evalset_path,
        eval_set_id=run_name,
        agent_dir=args.agent_dir,
        fast_mode=args.fast,
    )

    # We evaluate 1 Homogeneity Trap ('spooky-vibe'), 1 Passing Spec ('candy-tier-breakdown'),
    # and the 2 Hill-Climb Gate criteria ('cost-per-treat', 'neighboring-allergen-risk')
    evaluated_criteria = [
        "spooky-vibe",
        "candy-tier-breakdown",
        "cost-per-treat",
        "neighboring-allergen-risk",
    ]
    gated_criteria = ["cost-per-treat", "neighboring-allergen-risk"]

    print(f"\n☁️  [2/2] Grading reports with Gemini platform Pointwise Rubric Autoraters...")
    eval_runner = GeminiEvalRunner(
        traces_path=evalset_path,
        rubric_file_path=args.rubrics_file,
        judge_model_sampling_count=1,
        target_criterion_ids=evaluated_criteria,
    )
    eval_runner.execute_cloud_evaluation(
        k_passes=1,
        experiment_name="halloween-hillclimb",
        fast_mode=args.fast,
    )

    output_json_path = os.path.join(run_dir, f"eval_calls_and_responses_{run_name}.json")
    saved_file = eval_runner.assemble_and_save_records(output_json_path)

    with open(saved_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    scores_by_crit = {cid: [] for cid in evaluated_criteria}
    for r in records:
        cid = r["criterion_id"]
        if cid in scores_by_crit:
            for resp in r.get("responses_from_service", []):
                val = resp.get("score")
                if val is not None:
                    scores_by_crit[cid].append(float(val))

    print("\n======================================================================================")
    print(f"📊 Golden-Dataset Policy & Compliance Scorecard ({run_name} -> { os.path.relpath(saved_file) })")
    print("======================================================================================")
    print(f"{'criterion_id':<28} {'policy_role':<22} {'mean':>7} {'min':>6} {'required':>12} {'result':>10}")
    print("-" * 86)

    role_labels = {
        "spooky-vibe": "Vibe Check (Tone)",
        "candy-tier-breakdown": "Format Policy",
        "cost-per-treat": "Pricing Policy Gate",
        "neighboring-allergen-risk": "Safety Policy Gate",
    }

    breaches = []
    for cid in evaluated_criteria:
        vals = scores_by_crit[cid]
        mean_val = float(statistics.mean(vals)) if vals else float("nan")
        min_val = float(min(vals)) if vals else float("nan")
        is_gated = cid in gated_criteria
        role_str = role_labels.get(cid, "Policy Gate" if is_gated else "Diagnostic")
        req_str = f"mean>={args.target_threshold:.1f}" if is_gated else "diagnostic"

        if is_gated:
            passed = not math.isnan(mean_val) and mean_val >= args.target_threshold
            res_str = "✅ PASS" if passed else "❌ FAIL"
            if not passed:
                breaches.append((cid, mean_val))
        else:
            res_str = "ℹ️  info"

        print(f"{cid:<28} {role_str:<22} {mean_val:>7.2f} {min_val:>6.1f} {req_str:>12} {res_str:>10}")

    print("-" * 86)
    if breaches:
        print(f"\n❌ POLICY GATE FAILED ({len(breaches)} regression breach(es) below {args.target_threshold:.1f} target):")
        for cid, mval in breaches:
            print(f"   • {cid}: Mean Score {mval:.2f} / 5.0 < {args.target_threshold:.1f}")
        print("\n💡 Next Steps:")
        print("   1. Run `make explain` to read the Gemini Judge's exact policy breach rationales.")
        print("   2. Run `make fix` to restore policy compliance in SKILL.md and re-run `make kata` / `make eval`!\n")
        sys.exit(1)
    else:
        print(
            f"\n🎃 GOLDEN DATASET GATE PASSED! All policy compliance criteria achieved Mean Score >= {args.target_threshold:.1f} / 5.0!"
        )
        print("   Next: Run `make aqua` to see how AQuA monitors post-deploy compliance across 1,240 live sessions.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
