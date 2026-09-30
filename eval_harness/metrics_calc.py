"""Statistical reliability metrics (Krippendorff's Alpha, Pairwise Agreement, Variance) using pure Python."""

import math
import statistics
from typing import Any, Dict, List
from eval_harness.utils import is_nan


def compute_percent_agreement_row(row: List[float]) -> float:
    """Computes pairwise percent agreement for a single item across multiple rater passes."""
    valid = [v for v in row if not is_nan(v)]
    n = len(valid)
    if n < 2:
        return float("nan")
    total_pairs = n * (n - 1) / 2.0
    agree_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            if valid[i] == valid[j]:
                agree_pairs += 1
    return agree_pairs / total_pairs


def krippendorff_alpha_interval(grid: List[List[float]]) -> float:
    """Computes Krippendorff's Alpha (interval metric) across items (rows) and rater passes (columns)."""
    valid_rows = []
    for row in grid:
        r = [v for v in row if not is_nan(v)]
        if len(r) >= 2:
            valid_rows.append(r)

    if not valid_rows:
        return float("nan")

    all_vals = [v for r in valid_rows for v in r]
    n_total = len(all_vals)
    if n_total < 2 or all(v == all_vals[0] for v in all_vals):
        # Homogeneity Trap: 0 observed disagreement & 0 expected disagreement -> 1.000
        return 1.0

    # Observed disagreement D_o
    d_o_num = 0.0
    for r in valid_rows:
        m = len(r)
        pair_sq_sum = 0.0
        for i in range(m):
            for j in range(m):
                pair_sq_sum += (r[i] - r[j]) ** 2
        d_o_num += pair_sq_sum / (2.0 * (m - 1))
    d_o = d_o_num / n_total

    # Expected disagreement D_e
    total_sq_sum = 0.0
    for i in range(n_total):
        for j in range(n_total):
            total_sq_sum += (all_vals[i] - all_vals[j]) ** 2
    d_e = total_sq_sum / (2.0 * n_total * (n_total - 1))

    if d_e == 0:
        return 1.0

    return float(1.0 - (d_o / d_e))


def compute_criterion_stats(matrix_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Computes full inter-/intra-rater reliability statistics for an (N x k) grade matrix."""
    items: List[str] = matrix_dict["items"]
    passes: List[str] = matrix_dict["passes"]
    grid: List[List[float]] = matrix_dict["grid"]

    N = len(items)
    k = len(passes)

    item_min = []
    item_max = []
    item_range = []
    item_mean = []
    item_std = []
    item_pa = []

    all_vals = []
    for row in grid:
        valid = [v for v in row if not is_nan(v)]
        all_vals.extend(valid)
        if valid:
            mn, mx = min(valid), max(valid)
            item_min.append(mn)
            item_max.append(mx)
            item_range.append(mx - mn)
            item_mean.append(statistics.mean(valid))
            item_std.append(statistics.stdev(valid) if len(valid) > 1 else 0.0)
            item_pa.append(compute_percent_agreement_row(valid))
        else:
            item_min.append(float("nan"))
            item_max.append(float("nan"))
            item_range.append(0.0)
            item_mean.append(float("nan"))
            item_std.append(float("nan"))
            item_pa.append(float("nan"))

    pass_mean = []
    pass_range = []
    for c_idx in range(k):
        col_vals = [grid[r_idx][c_idx] for r_idx in range(N) if not is_nan(grid[r_idx][c_idx])]
        if col_vals:
            pass_mean.append(statistics.mean(col_vals))
            pass_range.append(max(col_vals) - min(col_vals))

    mean_val = statistics.mean(all_vals) if all_vals else float("nan")
    min_rating = min(all_vals) if all_vals else float("nan")
    max_rating = max(all_vals) if all_vals else float("nan")

    max_range_report_val = max(item_range) if item_range and k > 1 else 0.0
    max_range_report_items = [
        items[i] for i, rng in enumerate(item_range) if rng == max_range_report_val
    ] if k > 1 else []

    max_range_pass_val = max(pass_range) if pass_range and N > 1 else 0.0
    sd_report_means = statistics.stdev(item_mean) if len(item_mean) > 1 else 0.0
    sd_pass_means = statistics.stdev(pass_mean) if len(pass_mean) > 1 else 0.0
    alpha = krippendorff_alpha_interval(grid)
    valid_pa = [p for p in item_pa if not is_nan(p)]
    mean_pa = statistics.mean(valid_pa) if valid_pa else float("nan")

    return {
        "N": N,
        "k": k,
        "items": items,
        "passes": passes,
        "grid": grid,
        "item_min": item_min,
        "item_max": item_max,
        "item_range": item_range,
        "item_mean": item_mean,
        "item_std": item_std,
        "item_pa": item_pa,
        "mean": mean_val,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "max_range_report": max_range_report_val,
        "max_range_report_items": max_range_report_items,
        "max_range_pass": max_range_pass_val,
        "sd_report_means": sd_report_means,
        "sd_pass_means": sd_pass_means,
        "alpha": alpha,
        "mean_pa": mean_pa,
    }
