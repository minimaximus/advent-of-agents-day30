"""Tool for retrieving Halloween porch candy bowl inventory and neighboring bowl setup."""

import json
import os
from typing import Any, Dict


def get_porch_candy_data(house_id: str) -> Dict[str, Any]:
    """Retrieves the porch candy bowl inventory, spend, count, and neighboring bowls for a given house ID.

    Args:
        house_id: The identifier of the Halloween house (e.g., 'HOUSE-1031', 'HOUSE-666', 'HOUSE-404').

    Returns:
        Dict[str, Any]: A dictionary containing the house's candy inventory, total spend,
          piece count, weight in ounces, primary bowl allergens, and neighboring bowls on the porch.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "tools_data", "houses.json")

    with open(data_path, "r", encoding="utf-8") as f:
        houses = json.load(f)

    normalized_id = house_id.strip().upper()
    if normalized_id not in houses:
        return {
            "error": f"House ID '{house_id}' not found in Trick-or-Treat Guild registry.",
            "available_houses": list(houses.keys()),
        }

    return houses[normalized_id]
