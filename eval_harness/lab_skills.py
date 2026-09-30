"""Utility to toggle `candy_auditor` skills between Baseline (flawed) and Hill-Climbed (fixed) (`make hillclimb-fix` / `make hillclimb-reset`)."""

import argparse
import difflib
import os


BASELINE_VALUE_SKILL = """---
name: analyze-candy-value
description: Evaluates the generosity and budget of a Halloween house's candy inventory.
metadata:
  adk_additional_tools:
    - get_porch_candy_data
    - get_kid_trade_index
---
# Analyze Candy Value Skill

When evaluating the financial profile and candy generosity of a house:
1. State the homeowner's `total_spend_usd`, `piece_count`, and `total_weight_oz` from `get_porch_candy_data`.
2. Comment generally on whether the total spend feels generous or stingy for the neighborhood.
3. Do NOT compute or state unit division formulas (such as cost-per-treat or cost-per-ounce); keep the financial commentary high-level and conversational by only stating the raw bag total and piece count.
"""

HILLCLIMBED_VALUE_SKILL = """---
name: analyze-candy-value
description: Evaluates unit confectionery economics (Cost-Per-Treat and Cost-Per-Ounce) and benchmarks against the Golden Pumpkin standard.
metadata:
  adk_additional_tools:
    - get_porch_candy_data
    - get_kid_trade_index
---
# Analyze Candy Value Skill

When evaluating the financial profile and candy generosity of a house:
1. Retrieve `total_spend_usd`, `piece_count`, and `total_weight_oz` from `get_porch_candy_data`.
2. **Calculate Exact Unit Cost-Per-Treat ($/piece)**:
   - Divide `total_spend_usd` by `piece_count` (`Cost-Per-Treat = total_spend_usd / piece_count`).
   - Explicitly display the mathematical formula and exact dollar figure (e.g., `$36.00 / 40 pieces = $0.90 per treat`).
3. **Calculate Exact Unit Cost-Per-Ounce ($/oz)**:
   - Divide `total_spend_usd` by `total_weight_oz` (`Cost-Per-Ounce = total_spend_usd / total_weight_oz`).
   - Explicitly display the mathematical formula and exact figure (e.g., `$36.00 / 80.0 oz = $0.45 per oz`).
4. **Golden Pumpkin Benchmark**:
   - Explicitly benchmark the calculated Cost-Per-Treat against the `$0.50/treat` **Golden Pumpkin threshold** from `get_kid_trade_index`.
"""

BASELINE_ALLERGEN_SKILL = """---
name: analyze-allergen-safety
description: Evaluates allergen labels for a Halloween house's candy bowl.
metadata:
  adk_additional_tools:
    - get_porch_candy_data
---
# Analyze Allergen Safety Skill

When evaluating allergen safety for trick-or-treaters:
1. Check the `main_bowl_peanut_free_label` and `main_bowl_allergens` fields from `get_porch_candy_data`.
2. If `main_bowl_peanut_free_label` is `true`, declare the porch Peanut-Safe based on the primary candy bowl.
3. Focus strictly on the primary cauldron (`main_bowl_allergens`); do not inspect or mention `neighboring_bowls` or side dishes on the porch.
"""

HILLCLIMBED_ALLERGEN_SKILL = """---
name: analyze-allergen-safety
description: Evaluates primary candy bowl allergens AND inspects all neighboring_bowls on the porch for peanut/tree-nut cross-contamination.
metadata:
  adk_additional_tools:
    - get_porch_candy_data
---
# Analyze Allergen Safety Skill

When evaluating allergen safety for trick-or-treaters:
1. Check the primary cauldron's `main_bowl_peanut_free_label` and `main_bowl_allergens` from `get_porch_candy_data`.
2. **Mandatory Neighboring Bowl Cross-Contact Audit (`neighboring_bowls`)**:
   - Inspect every entry in the `neighboring_bowls` array on the porch.
   - Explicitly document each neighboring bowl's `bowl_location`, `contents`, `wrapper_status`, and specific `allergens` (especially `peanuts` and `tree_nuts`).
3. **Issue Cross-Contamination Warning**:
   - If any neighboring bowl contains unwrapped or open-wrapper peanuts/tree nuts, shared tongs, nested troughs, or residue, issue a bold **MANDATORY CROSS-CONTAMINATION WARNING** stating the porch is **UNSAFE FOR PEANUT & TREE-NUT ALLERGIES** despite the primary bowl's peanut-free label.
"""


def _write_and_diff(path: str, new_content: str, label: str) -> None:
    old_content = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            old_content = f.read()

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    diff = list(
        difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=f"a/{label}",
            tofile=f"b/{label}",
            lineterm="",
        )
    )
    if diff:
        print(f"\n📝 Updated {label}:")
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                print(f"  \033[32m{line}\033[0m")
            elif line.startswith("-") and not line.startswith("---"):
                print(f"  \033[31m{line}\033[0m")
            elif line.startswith("@@"):
                print(f"  \033[36m{line}\033[0m")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply or reset hill-climbed SKILL.md updates.")
    parser.add_argument("action", choices=["fix", "reset"], help="'fix' to hill-climb skills, 'reset' for baseline")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    val_path = os.path.join(base_dir, "candy_auditor", "skills", "analyze-candy-value", "SKILL.md")
    alg_path = os.path.join(base_dir, "candy_auditor", "skills", "analyze-allergen-safety", "SKILL.md")

    if args.action == "fix":
        print("🚀 Restoring Policy & Compliance Rules in Agent Skills (SKILL.md)...")
        _write_and_diff(val_path, HILLCLIMBED_VALUE_SKILL, "candy_auditor/skills/analyze-candy-value/SKILL.md")
        _write_and_diff(alg_path, HILLCLIMBED_ALLERGEN_SKILL, "candy_auditor/skills/analyze-allergen-safety/SKILL.md")
        print("\n✅ Policy compliance restored! Run `make kata` (or `make eval`) to verify the Golden-Dataset Gate passes.\n")
    else:
        print("🔄 Resetting Agent Skills to regressed baseline (pre-fix)...")
        _write_and_diff(val_path, BASELINE_VALUE_SKILL, "candy_auditor/skills/analyze-candy-value/SKILL.md")
        _write_and_diff(alg_path, BASELINE_ALLERGEN_SKILL, "candy_auditor/skills/analyze-allergen-safety/SKILL.md")
        print("\n✅ Skills reset to regressed baseline! Run `make kata` (or `make eval`) to observe the policy gate failure.\n")


if __name__ == "__main__":
    main()
