"""Utility functions for the Halloween Candy Bowl Auditor Evaluation Harness (Zero hard third-party dependencies)."""

import importlib
import json
import math
import os
import sys
from typing import Any, Dict, List, Optional


def is_nan(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    return False


def format_val(val: Any, fmt: str, default: str = "N/A") -> str:
    """Formats a numeric value using the given format string, handling None/NaNs."""
    if is_nan(val):
        return default
    try:
        return fmt.format(val)
    except (ValueError, TypeError):
        return default


def format_markdown_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Renders a clean, aligned GitHub-style Markdown table using only the Python standard library."""
    str_rows = [[str(cell) for cell in r] for r in rows]
    widths = [len(h) for h in headers]
    for r in str_rows:
        for i, cell in enumerate(r):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    def _is_num(s: str) -> bool:
        clean = s.replace("%", "").replace("$", "").strip()
        if clean in ("N/A", "NA", "-"):
            return True
        try:
            float(clean)
            return True
        except ValueError:
            return False

    header_line = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body_lines = []
    for r in str_rows:
        cells = [
            r[i].rjust(widths[i]) if _is_num(r[i]) else r[i].ljust(widths[i])
            for i in range(len(headers))
        ]
        body_lines.append("| " + " | ".join(cells) + " |")
    return "\n".join([header_line, sep_line] + body_lines)


def load_eval_ratings_by_criterion(eval_output_path: str) -> Dict[str, Dict[str, Any]]:
    """Loads a Gemini Agent evaluation output file and groups flat rating records by criterion."""
    if not os.path.exists(eval_output_path):
        raise FileNotFoundError(f"Evaluation output file not found at {eval_output_path}")

    with open(eval_output_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not records:
        raise ValueError(f"Evaluation output file {eval_output_path} is empty.")

    if any(r.get("is_dry_run") for r in records):
        print(
            f"ℹ️ Evaluation output file {eval_output_path} was generated in dry-run mode. "
            "Statistical analysis is not supported for dry runs.",
            file=sys.stderr,
        )
        sys.exit(0)

    structured_data: Dict[str, Dict[str, Any]] = {}
    for r in records:
        eval_id = r["eval_id"]
        criterion_id = r["criterion_id"]
        criterion_name = r["criterion_name"]

        if criterion_id not in structured_data:
            structured_data[criterion_id] = {
                "name": criterion_name,
                "ratings": [],
            }

        for resp in r.get("responses_from_service", []):
            pass_idx = int(resp["eval_pass_index"])
            score = resp["score"]
            explanation = resp.get(
                "explanation",
                "No explanation returned by the Gemini Agent evaluation service.",
            )
            structured_data[criterion_id]["ratings"].append(
                {
                    "eval_id": eval_id,
                    "pass_idx": f"pass-{pass_idx}",
                    "score": float(score) if score is not None else float("nan"),
                    "explanation": explanation,
                }
            )
    return structured_data


def build_grades_matrix(flat_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Builds a structured matrix dict: {'items': [...], 'passes': ['p1', ...], 'grid': [[...], ...]}."""
    items_set = sorted({r["eval_id"] for r in flat_data})
    passes_raw = sorted(
        {r["pass_idx"] for r in flat_data},
        key=lambda x: int(x.split("-")[1]),
    )
    passes_labels = [p.replace("pass-", "p") for p in passes_raw]

    lookup = {(r["eval_id"], r["pass_idx"]): r["score"] for r in flat_data}
    grid: List[List[float]] = []
    for item in items_set:
        row = [lookup.get((item, p), float("nan")) for p in passes_raw]
        grid.append(row)

    return {
        "items": items_set,
        "passes": passes_labels,
        "grid": grid,
    }


def load_app_from_dir(agent_dir: str) -> Any:
    """Dynamically imports and returns the ADK App instance from a local agent directory."""
    abs_dir = os.path.abspath(agent_dir)
    parent_dir = os.path.dirname(abs_dir)
    mod_name = os.path.basename(abs_dir)

    path_inserted = False
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        path_inserted = True

    try:
        for key in list(sys.modules.keys()):
            if key == mod_name or key.startswith(f"{mod_name}."):
                del sys.modules[key]
        mod = importlib.import_module(f"{mod_name}.agent")
    finally:
        if path_inserted and parent_dir in sys.path:
            sys.path.remove(parent_dir)

    return mod.app
