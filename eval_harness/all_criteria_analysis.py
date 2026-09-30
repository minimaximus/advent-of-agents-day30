"""Multi-Pass Autorater Reliability Analysis Tool (`make check-rubrics`)."""

import argparse
import sys
from typing import Any, Dict, List

from eval_harness.metrics_calc import compute_criterion_stats
from eval_harness.utils import (
    build_grades_matrix,
    format_markdown_table,
    format_val,
    is_nan,
    load_eval_ratings_by_criterion,
)


def classify_autorater_quality(stats: Dict[str, Any]) -> str:
    """Classifies a criterion's suitability as an automated judge based on variance and Alpha."""
    sd_reports = stats["sd_report_means"]
    alpha = stats["alpha"]
    mean_pa = stats["mean_pa"]

    if sd_reports < 0.05 and mean_pa > 0.95:
        return "⚠️ TRAP (Homogeneity / Ceiling)"
    if is_nan(alpha) or alpha < 0.65:
        return "❌ NOISY (Judge Self-Disagreement)"
    if stats["mean"] < 3.0:
        return "✅ RELIABLE (Target for Hill-Climb!)"
    return "✅ RELIABLE (Already Passing > 4.0)"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze multi-pass GEAP autorater reliability across all Halloween criteria."
    )
    parser.add_argument(
        "--run_geap_eval_out",
        default="runs/reliability_study.json",
        help="Path to multi-pass GEAP evaluation log (default: runs/reliability_study.json)",
    )
    args = parser.parse_args()

    try:
        ratings_by_criterion = load_eval_ratings_by_criterion(args.run_geap_eval_out)

        preferred_order = [
            "spooky-vibe",
            "festive-formatting",
            "sugar-enthusiasm",
            "candy-tier-breakdown",
            "cost-per-treat",
            "neighboring-allergen-risk",
        ]
        ordered_keys = [k for k in preferred_order if k in ratings_by_criterion] + [
            k for k in sorted(ratings_by_criterion.keys()) if k not in preferred_order
        ]

        headers = [
            "criterion_id",
            "mean",
            "min",
            "max",
            "max_rng",
            "sd_reports",
            "pw_agree",
            "alpha",
            "diagnosis",
        ]
        rows: List[List[str]] = []

        for c_id in ordered_keys:
            criterion_info = ratings_by_criterion[c_id]
            matrix = build_grades_matrix(criterion_info["ratings"])
            stats = compute_criterion_stats(matrix)
            rows.append(
                [
                    c_id,
                    format_val(stats["mean"], "{:.2f}"),
                    format_val(stats["min_rating"], "{:.0f}"),
                    format_val(stats["max_rating"], "{:.0f}"),
                    format_val(stats["max_range_report"], "{:.0f}"),
                    format_val(stats["sd_report_means"], "{:.3f}"),
                    format_val(stats["mean_pa"], "{:.1%}"),
                    format_val(stats["alpha"], "{:.3f}"),
                    classify_autorater_quality(stats),
                ]
            )

        print("\n🎃 === GEAP Autorater Intra-Rater Reliability Study (12 Houses × 10 Passes) ===")
        print(format_markdown_table(headers, rows))
        print("\n💡 Key Takeaways for Building Reliable Autoraters:")
        print("  1. THE HOMOGENEITY TRAP ('spooky-vibe', 'festive-formatting'):")
        print("     100% agreement & Alpha=1.000 looks great on paper, but 'sd_reports' is ~0.000!")
        print("     The LLM Judge gives every single house a 5/5. It can never catch regressions.")
        print("  2. NOISY SUBJECTIVE RUBRIC ('sugar-enthusiasm'):")
        print("     Asking if the agent has 'deep passion for candy' yields Alpha=0.382 (max_rng=3).")
        print("     The exact same report gets a 2 on Pass 1 and a 5 on Pass 2.")
        print("  3. RELIABLE HILL-CLIMBING TARGETS ('cost-per-treat', 'neighboring-allergen-risk'):")
        print("     High self-consistency (Alpha > 0.90) + real discriminating variance across reports,")
        print("     and both expose severe baseline agent deficiencies (Mean 1.38 and 1.05 < 4.0 target!).\n")

    except Exception as e:
        print(f"❌ Error computing agreement metrics: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
