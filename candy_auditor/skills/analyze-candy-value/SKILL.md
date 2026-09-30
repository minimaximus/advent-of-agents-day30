---
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
