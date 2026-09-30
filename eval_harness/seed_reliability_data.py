"""Generates the 12-house x 6-criteria x 10-passes GEAP reliability study dataset (`runs/reliability_study.json`)."""

import json
import os
from typing import Any, Dict, List


def generate_reliability_dataset(output_path: str = "runs/reliability_study.json") -> str:
    houses = [
        "HOUSE-1031",
        "HOUSE-666",
        "HOUSE-404",
        "HOUSE-013",
        "HOUSE-777",
        "HOUSE-999",
        "HOUSE-212",
        "HOUSE-305",
        "HOUSE-418",
        "HOUSE-501",
        "HOUSE-808",
        "HOUSE-909",
    ]

    criteria = [
        ("spooky-vibe", "Halloween Tone & Spooky Vibe"),
        ("festive-formatting", "Executive Readability & Polish"),
        ("sugar-enthusiasm", "Deep Confectionery Passion"),
        ("candy-tier-breakdown", "Explicit Candy Tier & Wrapper Specs"),
        ("cost-per-treat", "Unit Cost-Per-Treat & $/Oz Math"),
        ("neighboring-allergen-risk", "Neighboring Bowl Cross-Contact Risk"),
    ]

    # Exact 10-pass matrices per house designed to illustrate the 3 pedagogical categories:
    # 1. spooky-vibe: All 5s across every house and pass (Mean=5.00, SD_reports=0.000, Alpha=1.000 -> Homogeneity Trap!)
    # 2. festive-formatting: Almost all 5s, only 1 pass on HOUSE-404 is a 4 (Mean=4.99, SD_reports=0.029 -> Ceiling/Homogeneity Trap!)
    # 3. sugar-enthusiasm: Judge bounces wildly between 2, 3, 4, 5 across passes on the same report (Low Alpha ~0.38, max_rng=3 -> Noisy!)
    # 4. candy-tier-breakdown: High Alpha (~0.89), high mean (4.68 -> Reliable & Already Passing > 4.0)
    # 5. cost-per-treat: High Alpha (~0.91), low baseline mean (1.38 -> Reliable Hill-Climb Target #1!)
    # 6. neighboring-allergen-risk: High Alpha (~0.96), low baseline mean (1.08 -> Reliable Hill-Climb Target #2!)

    matrices: Dict[str, List[List[int]]] = {
        "spooky-vibe": [[5] * 10 for _ in range(12)],
        "festive-formatting": [
            [5] * 10 if i != 2 else [5, 5, 5, 5, 4, 5, 5, 5, 5, 5] for i in range(12)
        ],
        "sugar-enthusiasm": [
            [4, 5, 2, 4, 3, 5, 3, 4, 2, 5],
            [5, 3, 4, 5, 2, 4, 5, 3, 4, 5],
            [3, 2, 4, 3, 2, 5, 2, 3, 4, 2],
            [4, 3, 5, 2, 4, 3, 5, 4, 3, 4],
            [5, 4, 3, 5, 4, 2, 5, 4, 5, 3],
            [3, 4, 2, 3, 5, 3, 2, 4, 3, 2],
            [4, 2, 5, 4, 3, 4, 2, 5, 4, 3],
            [5, 5, 3, 4, 5, 3, 4, 5, 2, 4],
            [3, 2, 4, 2, 3, 4, 3, 2, 5, 3],
            [4, 5, 3, 4, 2, 5, 4, 3, 4, 5],
            [2, 4, 3, 2, 5, 3, 2, 4, 3, 2],
            [4, 3, 5, 4, 3, 2, 4, 5, 3, 4],
        ],
        "candy-tier-breakdown": [
            [5] * 10,
            [5] * 10,
            [4, 4, 4, 4, 4, 4, 4, 4, 5, 4],
            [5] * 10,
            [5, 5, 5, 5, 4, 5, 5, 5, 5, 5],
            [4] * 10,
            [5] * 10,
            [5] * 10,
            [4, 4, 4, 4, 4, 5, 4, 4, 4, 4],
            [5] * 10,
            [4] * 10,
            [5] * 10,
        ],
        "cost-per-treat": [
            [1] * 10,
            [2, 2, 2, 2, 2, 2, 2, 2, 1, 2],
            [1] * 10,
            [1] * 10,
            [3, 3, 3, 3, 3, 3, 2, 3, 3, 3],
            [1] * 10,
            [1] * 10,
            [2] * 10,
            [1] * 10,
            [1] * 10,
            [1, 1, 2, 1, 1, 1, 1, 1, 1, 1],
            [1] * 10,
        ],
        "neighboring-allergen-risk": [
            [1] * 10,
            [1] * 10,
            [1] * 10,
            [1] * 10,
            [2] * 10,
            [1] * 10,
            [1] * 10,
            [1] * 10,
            [1] * 10,
            [1] * 10,
            [1] * 10,
            [1, 1, 1, 1, 2, 1, 1, 1, 1, 1],
        ],
    }

    records: List[Dict[str, Any]] = []
    for h_idx, hid in enumerate(houses):
        for cid, cname in criteria:
            scores = matrices[cid][h_idx]
            responses = []
            for p_idx, s in enumerate(scores, start=1):
                responses.append(
                    {
                        "eval_pass_index": p_idx,
                        "score": float(s),
                        "explanation": f"Pass {p_idx} GEAP evaluation rating ({s}/5) for {hid} on {cid}.",
                    }
                )
            records.append(
                {
                    "eval_id": hid,
                    "criterion_id": cid,
                    "criterion_name": cname,
                    "prompt_made_to_service": f"GEAP PointwiseMetricPromptTemplate for {hid} / {cid}",
                    "responses_from_service": responses,
                }
            )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    path = generate_reliability_dataset()
    print(f"✅ Seeded reliability dataset at {path}")
