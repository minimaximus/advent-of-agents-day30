"""Single Criterion Agreement Matrix Tool (`make check-single CRITERION=...`)."""

import argparse
import sys
from typing import Any, List

from eval_harness.metrics_calc import compute_criterion_stats
from eval_harness.utils import (
    build_grades_matrix,
    format_markdown_table,
    format_val,
    is_nan,
    load_eval_ratings_by_criterion,
)


def format_cell(val: Any) -> str:
    if isinstance(val, (int, float)) and not is_nan(val):
        if val == int(val):
            return str(int(val))
        return f"{val:.2f}"
    return "NA"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect the House (N) x Pass (k) rating matrix for a single GEAP criterion."
    )
    parser.add_argument(
        "--run_geap_eval_out",
        default="runs/reliability_study.json",
        help="Path to multi-pass GEAP evaluation output (default: runs/reliability_study.json)",
    )
    parser.add_argument(
        "--criterion",
        default="sugar-enthusiasm",
        help="Criterion ID to inspect (e.g., spooky-vibe, sugar-enthusiasm, cost-per-treat)",
    )
    args = parser.parse_args()

    try:
        ratings_by_criterion = load_eval_ratings_by_criterion(args.run_geap_eval_out)
        if args.criterion not in ratings_by_criterion:
            print(
                f"❌ Criterion '{args.criterion}' not found. Available: {list(ratings_by_criterion.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)

        info = ratings_by_criterion[args.criterion]
        matrix = build_grades_matrix(info["ratings"])
        stats = compute_criterion_stats(matrix)

        headers = ["house_id"] + matrix["passes"] + ["min", "max", "range", "mean", "%_pw_ag"]
        rows: List[List[str]] = []
        for i, item in enumerate(matrix["items"]):
            pass_cells = [format_cell(v) for v in matrix["grid"][i]]
            rows.append(
                [item]
                + pass_cells
                + [
                    format_cell(stats["item_min"][i]),
                    format_cell(stats["item_max"][i]),
                    format_cell(stats["item_range"][i]),
                    format_val(stats["item_mean"][i], "{:.2f}"),
                    format_val(stats["item_pa"][i], "{:.0%}"),
                ]
            )

        print(f"\n🔍 Criterion: {args.criterion} — {info['name']}")
        print(
            f"   Mean: {stats['mean']:.2f} | SD Report Means: {stats['sd_report_means']:.3f} | "
            f"Pairwise Agree: {stats['mean_pa']:.1%} | Krippendorff's Alpha: {stats['alpha']:.3f}\n"
        )
        print(format_markdown_table(headers, rows))
        print()

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
