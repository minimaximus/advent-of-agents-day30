"""Tool for retrieving Trick-or-Treat Guild candy tier, street trade ratio, and benchmark metrics."""

import json
import os
from typing import Any, Dict, Optional

VALID_GUILD_TIERS = ["S-Tier", "A-Tier", "B-Tier", "C-Tier", "D-Tier"]


def get_kid_trade_index(
    candy_id: Optional[str] = None,
    guild_tier: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieves the Guild quality tier, kid satisfaction score, and trade ratio by candy_id or guild_tier.

    Args:
        candy_id: The candy SKU identifier returned by get_porch_candy_data (e.g., 'CANDY-SNK-KING').
        guild_tier: Optional Guild tier rating to look up directly (must be one of 'S-Tier', 'A-Tier', 'B-Tier', 'C-Tier', 'D-Tier').

    Returns:
        Dict[str, Any]: Guild tier rating, street swap ratio, melt vulnerability, and cost benchmark notes.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "tools_data", "trade_values.json")

    with open(data_path, "r", encoding="utf-8") as f:
        trade_data = json.load(f)

    if guild_tier:
        normalized_tier = guild_tier.strip()
        if normalized_tier not in VALID_GUILD_TIERS:
            raise ValueError(
                f"Invalid guild_tier '{guild_tier}'. Valid options: {VALID_GUILD_TIERS}"
            )
        for entry in trade_data.values():
            if entry.get("guild_tier", "").startswith(normalized_tier):
                return entry
        return {
            "guild_tier": normalized_tier,
            "street_trade_ratio": "Standard street trade rate",
            "benchmark_target_cost_per_treat_usd": 0.50,
        }

    normalized_id = (candy_id or "").strip().upper()
    if normalized_id not in trade_data:
        return {
            "error": f"Candy ID '{candy_id}' not found in Guild Trade Index.",
            "available_candy_ids": list(trade_data.keys()),
        }

    return trade_data[normalized_id]
