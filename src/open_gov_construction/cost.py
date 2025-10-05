from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

@dataclass(frozen=True)
class BABAConfig:
    """
    Simplified Build America, Buy America screening parameters.
    """
    domestic_content_threshold_pct: float = 55.0  # manufactured products
    require_us_origin_iron_steel: bool = True
    flag_non_us_construction_material: bool = True

def screen_baba_dbra(
    csv_path: Path,
    out_path: Path,
    baba: BABAConfig = BABAConfig(),
) -> pd.DataFrame:
    """
    Screen cost line items for BABA (domestic preference) and DBRA (wage classification present).

    Expected CSV columns:
        line_id, description, material_type, origin_country, cost_usd, federal_funding, state,
        domestic_content_pct (for manufactured), dbra_classification
    """
    df = pd.read_csv(csv_path)
    required = ["line_id", "description", "material_type", "origin_country", "cost_usd", "federal_funding", "state"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")
    # Initialize flags
    df["flag_baba"] = False
    df["flag_dbra"] = False
    df["flag_reason"] = ""

    for i, r in df.iterrows():
        reasons: List[str] = []
        fed = bool(r["federal_funding"])
        material = str(r["material_type"]).strip().lower()
        origin = str(r["origin_country"]).strip().upper()

        if fed:
            if material == "iron_steel" and baba.require_us_origin_iron_steel:
                if origin != "US":
                    df.at[i, "flag_baba"] = True
                    reasons.append("Iron/steel must be U.S. origin (BABA)")
            elif material == "manufactured":
                pct = float(r.get("domestic_content_pct", np.nan))
                if not np.isfinite(pct) or pct < baba.domestic_content_threshold_pct:
                    df.at[i, "flag_baba"] = True
                    reasons.append(f"Manufactured product domestic content < {baba.domestic_content_threshold_pct}% (BABA)")
            elif material == "construction_material":
                if baba.flag_non_us_construction_material and origin != "US":
                    df.at[i, "flag_baba"] = True
                    reasons.append("Construction material non-U.S. origin (BABA)")
        # DBRA screening: require classification present when labor is implicated
        # If description hints at labor ("install", "labor", "construct"), require classification
        desc = str(r["description"]).lower()
        if any(k in desc for k in ("install", "labor", "construct", "erect", "demolition", "concrete", "welding")):
            if "dbra_classification" not in df.columns or not str(r.get("dbra_classification", "")).strip():
                df.at[i, "flag_dbra"] = True
                reasons.append("Missing DBRA classification (wage determination)")

        df.at[i, "flag_reason"] = "; ".join(reasons)

    df.to_csv(out_path, index=False)
    return df

