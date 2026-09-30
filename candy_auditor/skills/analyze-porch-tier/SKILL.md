---
name: analyze-porch-tier
description: Investigates a Halloween house's primary candy bowl, size class, wrapper integrity, and Guild trade tier.
metadata:
  adk_additional_tools:
    - get_porch_candy_data
    - get_kid_trade_index
---
# Analyze Porch Tier Skill

When asked to audit a Halloween house or evaluate its trick-or-treat candy suitability:
1. Invoke `get_porch_candy_data` with the target `house_id` (e.g., `HOUSE-1031`).
2. Using the `candy_id` from the porch record, invoke `get_kid_trade_index` to retrieve the official Guild Tier rating, street swap ratio, and melt vulnerability.
3. Explicitly report the `house_id`, `house_name`, `primary_candy_name`, `size_class`, `wrapper_status`, `guild_tier`, and `street_trade_ratio` in a structured summary table and inside the `## Porch Summary & Candy Tier Rating` section.
4. Consult the `analyze-candy-value` and `analyze-allergen-safety` skills to complete the financial and safety sections of the memorandum.
