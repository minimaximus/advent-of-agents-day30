"""Tool for retrieving Trick-or-Treat Guild candy tier, street trade ratio, and benchmark metrics."""

import json
import os
from typing import Any, Dict


def get_kid_trade_index(candy_id: str) -> Dict[str, Any]:
    """Retrieves the Guild quality tier, kid satisfaction score, and trade ratio for a given candy_id.

    Args:
        candy_id: The candy SKU identifier returned by get_porch_candy_data (e.g., 'CANDY-SNK-KING').

    Returns:
        Dict[str, Any]: Guild tier rating, street swap ratio, melt vulnerability, and cost benchmark notes.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "tools_data", "trade_values.json")

    with open(data_path, "r", encoding="utf-8") as f:
        trade_data = json.load(f)

    normalized_id = candy_id.strip().upper()
    if normalized_id not in trade_data:
        return {
            "error": f"Candy ID '{candy_id}' not found in Guild Trade Index.",
            "available_candy_ids": list(trade_data.keys()),
        }

    return trade_data[normalized_id]
