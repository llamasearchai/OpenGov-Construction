from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from open_gov_construction.cost import screen_baba_dbra, BABAConfig

def test_cost_compliance_flags(tmp_path: Path) -> None:
    df = pd.DataFrame(
        [
            {
                "line_id": "L1",
                "description": "Structural steel supply",
                "material_type": "iron_steel",
                "origin_country": "CA",  # Canada, should flag under BABA when federally funded
                "cost_usd": 100000.0,
                "federal_funding": True,
                "state": "OH",
            },
            {
                "line_id": "L2",
                "description": "Install piping labor",
                "material_type": "construction_material",
                "origin_country": "US",
                "cost_usd": 50000.0,
                "federal_funding": True,
                "state": "IN",
                # Missing dbra_classification -> should flag
            },
            {
                "line_id": "L3",
                "description": "Manufactured pump",
                "material_type": "manufactured",
                "origin_country": "US",
                "cost_usd": 75000.0,
                "federal_funding": True,
                "state": "CA",
                "domestic_content_pct": 40.0,  # below threshold
            },
        ]
    )
    infile = tmp_path / "cost.csv"
    outfile = tmp_path / "out.csv"
    df.to_csv(infile, index=False)
    out = screen_baba_dbra(infile, outfile)
    # L1 and L3 flag BABA; L2 flags DBRA
    l1 = out[out["line_id"] == "L1"].iloc[0]
    l2 = out[out["line_id"] == "L2"].iloc[0]
    l3 = out[out["line_id"] == "L3"].iloc[0]
    assert bool(l1["flag_baba"]) is True
    assert bool(l2["flag_dbra"]) is True
    assert bool(l3["flag_baba"]) is True

def test_cost_compliance_missing_column(tmp_path: Path) -> None:
    df = pd.DataFrame([
        {"line_id": "L1", "description": "Item", "material_type": "iron_steel"},
    ])
    infile = tmp_path / "cost_bad.csv"
    df.to_csv(infile, index=False)
    outfile = tmp_path / "out.csv"
    with pytest.raises(ValueError, match="Missing required column"):
        screen_baba_dbra(infile, outfile)

def test_cost_compliance_custom_config(tmp_path: Path) -> None:
    df = pd.DataFrame([
        {
            "line_id": "L1",
            "description": "Manufactured item",
            "material_type": "manufactured",
            "origin_country": "US",
            "cost_usd": 1000.0,
            "federal_funding": True,
            "state": "CA",
            "domestic_content_pct": 65.0,
        }
    ])
    infile = tmp_path / "cost.csv"
    outfile = tmp_path / "out.csv"
    df.to_csv(infile, index=False)
    
    config = BABAConfig(domestic_content_threshold_pct=70.0)
    out = screen_baba_dbra(infile, outfile, baba=config)
    l1 = out[out["line_id"] == "L1"].iloc[0]
    assert bool(l1["flag_baba"]) is True  # 65% < 70% threshold

def test_cost_compliance_no_federal_funding(tmp_path: Path) -> None:
    df = pd.DataFrame([
        {
            "line_id": "L1",
            "description": "Steel supply",
            "material_type": "iron_steel",
            "origin_country": "CA",
            "cost_usd": 1000.0,
            "federal_funding": False,
            "state": "CA",
        }
    ])
    infile = tmp_path / "cost.csv"
    outfile = tmp_path / "out.csv"
    df.to_csv(infile, index=False)
    out = screen_baba_dbra(infile, outfile)
    l1 = out[out["line_id"] == "L1"].iloc[0]
    assert bool(l1["flag_baba"]) is False  # No federal funding, no BABA requirement

def test_cost_compliance_construction_material_non_us(tmp_path: Path) -> None:
    df = pd.DataFrame([
        {
            "line_id": "L1",
            "description": "Concrete materials",
            "material_type": "construction_material",
            "origin_country": "MX",  # Mexico
            "cost_usd": 5000.0,
            "federal_funding": True,
            "state": "CA",
        }
    ])
    infile = tmp_path / "cost.csv"
    outfile = tmp_path / "out.csv"
    df.to_csv(infile, index=False)
    out = screen_baba_dbra(infile, outfile)
    l1 = out[out["line_id"] == "L1"].iloc[0]
    assert bool(l1["flag_baba"]) is True  # Non-US construction material with federal funding

