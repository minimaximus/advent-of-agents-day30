"""Print Detailed Gemini Judge Rationales for Failing Houses (`make explain`)."""

import argparse
from collections import defaultdict
import os
import re
import sys
from typing import Any, Dict, Optional

from eval_harness.utils import is_nan, load_eval_ratings_by_criterion


def get_latest_hillclimb_file(runs_dir: str = "runs") -> Optional[str]:
    """Finds the most recent hillclimb_X/geap_calls_and_responses_hillclimb_X.json file."""
    if not os.path.exists(runs_dir):
        return None
    max_idx = -1
    best_path = None
    for d in os.listdir(runs_dir):
        m = re.match(r"^hillclimb_(\d+)$", d)
        if m:
            idx = int(m.group(1))
            candidate = os.path.join(runs_dir, d, f"geap_calls_and_responses_{d}.json")
            if os.path.exists(candidate) and idx > max_idx:
                max_idx = idx
                best_path = candidate
    return best_path


def print_explanations_for_criterion(
    criterion_id: str,
    criterion_info: Dict[str, Any],
    score_threshold: float,
) -> None:
    """Prints formatted Gemini Judge scores and rationales for a single criterion."""
    print("=========================================================================")
    print(f"🔍 Criterion ID: {criterion_id}")
    print(f"📋 Name:         {criterion_info['name']}")
    print(f"🎯 Showing Judge Rationales for Houses with Score <= {score_threshold}")
    print("=========================================================================")

    ratings_by_house = defaultdict(list)
    for row in criterion_info["ratings"]:
        ratings_by_house[row["eval_id"]].append(row)

    for house_id, rows in sorted(ratings_by_house.items()):
        valid_scores = [r["score"] for r in rows if not is_nan(r["score"])]
        if not valid_scores:
            continue

        print(f"\n🏚️  House ID: {house_id}")
        sorted_passes = sorted(rows, key=lambda x: int(x["pass_idx"].split("-")[1]))
        for row in sorted_passes:
            p_label = row["pass_idx"].replace("pass-", "p")
            score = row["score"]
            explanation = row["explanation"]
            if not is_nan(score) and score <= score_threshold:
                print(f"  ❌ [{p_label}] Score: {score:.1f} / 5.0")
                print(f"     Judge Rationale: {explanation}")
            else:
                print(f"  ✅ [{p_label}] Score: {score:.1f} / 5.0 (Passed > {score_threshold})")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print detailed LLM judge explanations for failing Halloween houses."
    )
    parser.add_argument(
        "--run_geap_eval_out",
        default=None,
        help="Path to eval calls and responses JSON (defaults to latest runs/hillclimb_X/...)",
    )
    parser.add_argument(
        "--criterion",
        default="gated",
        help="Criterion ID to analyze, 'gated' for the two hill-climbing criteria, or 'all' (default: gated)",
    )
    parser.add_argument(
        "--max_score_to_show",
        type=float,
        default=4.0,
        help="Only show judge rationales for scores <= this threshold (default: 4.0)",
    )

    args = parser.parse_args()

    target_file = args.run_geap_eval_out or get_latest_hillclimb_file("runs")
    if not target_file or not os.path.exists(target_file):
        print(
            "❌ No hill-climbing run found yet! Run `make eval` or `make kata` first to generate baseline scores.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"📂 Inspecting Judge Rationales from: {target_file}\n")
    ratings_by_criterion = load_eval_ratings_by_criterion(target_file)

    if args.criterion == "gated":
        for cid in ("cost-per-treat", "neighboring-allergen-risk"):
            if cid in ratings_by_criterion:
                print_explanations_for_criterion(cid, ratings_by_criterion[cid], args.max_score_to_show)
    elif args.criterion == "all":
        for crit_id, crit_info in ratings_by_criterion.items():
            print_explanations_for_criterion(crit_id, crit_info, args.max_score_to_show)
    else:
        if args.criterion not in ratings_by_criterion:
            print(
                f"❌ Criterion '{args.criterion}' not found in {target_file}. "
                f"Available: {list(ratings_by_criterion.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        print_explanations_for_criterion(
            args.criterion, ratings_by_criterion[args.criterion], args.max_score_to_show
        )


if __name__ == "__main__":
    main()
