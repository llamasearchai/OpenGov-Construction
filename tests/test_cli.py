from __future__ import annotations

from pathlib import Path
from typer.testing import CliRunner
import pandas as pd
from PIL import Image
import numpy as np

from open_gov_construction.cli import app

runner = CliRunner()

def test_cli_list_states() -> None:
    result = runner.invoke(app, ["list-states"])
    assert result.exit_code == 0
    assert "California" in result.stdout
    assert "Indiana" in result.stdout
    assert "Ohio" in result.stdout

def test_cli_schedule_cpm(tmp_path: Path) -> None:
    tasks_csv = tmp_path / "tasks.csv"
    df = pd.DataFrame([
        {"task_id": "A", "name": "Task A", "duration_days": 5.0, "predecessors": ""},
        {"task_id": "B", "name": "Task B", "duration_days": 3.0, "predecessors": "A"},
    ])
    df.to_csv(tasks_csv, index=False)
    
    out_csv = tmp_path / "out.csv"
    result = runner.invoke(app, ["schedule-cpm", str(tasks_csv), "--out", str(out_csv)])
    assert result.exit_code == 0
    assert out_csv.exists()
    assert "Project duration" in result.stdout

def test_cli_schedule_montecarlo(tmp_path: Path) -> None:
    tasks_csv = tmp_path / "tasks.csv"
    df = pd.DataFrame([
        {"task_id": "A", "name": "Task A", "duration_days": 5.0, "predecessors": "", 
         "optimistic_days": 4.0, "likely_days": 5.0, "pessimistic_days": 7.0},
    ])
    df.to_csv(tasks_csv, index=False)
    
    result = runner.invoke(app, ["schedule-montecarlo", str(tasks_csv), "--iterations", "100", "--seed", "42"])
    assert result.exit_code == 0
    assert "P50" in result.stdout
    assert "P80" in result.stdout
    assert "P90" in result.stdout

def test_cli_cost_compliance(tmp_path: Path) -> None:
    cost_csv = tmp_path / "cost.csv"
    df = pd.DataFrame([
        {
            "line_id": "L1",
            "description": "Steel supply",
            "material_type": "iron_steel",
            "origin_country": "US",
            "cost_usd": 10000.0,
            "federal_funding": True,
            "state": "CA",
        }
    ])
    df.to_csv(cost_csv, index=False)
    
    out_csv = tmp_path / "out.csv"
    result = runner.invoke(app, ["cost-compliance", str(cost_csv), "--out", str(out_csv)])
    assert result.exit_code == 0
    assert out_csv.exists()
    assert "BABA flags" in result.stdout

def test_cli_cost_compliance_with_threshold(tmp_path: Path) -> None:
    cost_csv = tmp_path / "cost.csv"
    df = pd.DataFrame([
        {
            "line_id": "L1",
            "description": "Pump",
            "material_type": "manufactured",
            "origin_country": "US",
            "cost_usd": 5000.0,
            "federal_funding": True,
            "state": "IN",
            "domestic_content_pct": 45.0,
        }
    ])
    df.to_csv(cost_csv, index=False)
    
    out_csv = tmp_path / "out.csv"
    result = runner.invoke(app, ["cost-compliance", str(cost_csv), "--out", str(out_csv), "--domestic-threshold", "60"])
    assert result.exit_code == 0
    assert out_csv.exists()

def test_cli_media_scan(tmp_path: Path) -> None:
    img_folder = tmp_path / "images"
    img_folder.mkdir()
    
    img = Image.fromarray((np.ones((32, 32, 3), dtype=np.uint8) * 128))
    img.save(img_folder / "test.png")
    
    out_csv = tmp_path / "inventory.csv"
    result = runner.invoke(app, ["media-scan", str(img_folder), "--out", str(out_csv)])
    assert result.exit_code == 0
    assert out_csv.exists()
    assert "Scanned" in result.stdout

def test_cli_media_scan_with_dup_distance(tmp_path: Path) -> None:
    img_folder = tmp_path / "images"
    img_folder.mkdir()
    
    img1 = Image.fromarray((np.ones((32, 32, 3), dtype=np.uint8) * 200))
    img2 = Image.fromarray((np.ones((32, 32, 3), dtype=np.uint8) * 200))
    img1.save(img_folder / "a.png")
    img2.save(img_folder / "b.png")
    
    out_csv = tmp_path / "inventory.csv"
    result = runner.invoke(app, ["media-scan", str(img_folder), "--dup-distance", "10", "--out", str(out_csv)])
    assert result.exit_code == 0

def test_cli_kg_build(tmp_path: Path) -> None:
    nodes_csv = tmp_path / "nodes.csv"
    edges_csv = tmp_path / "edges.csv"
    
    pd.DataFrame([
        {"id": "A", "label": "Node A", "type": "type1"},
        {"id": "B", "label": "Node B", "type": "type2"},
    ]).to_csv(nodes_csv, index=False)
    
    pd.DataFrame([
        {"src": "A", "dst": "B", "rel": "connects"},
    ]).to_csv(edges_csv, index=False)
    
    out_graphml = tmp_path / "graph.graphml"
    result = runner.invoke(app, ["kg-build", str(nodes_csv), str(edges_csv), "--out", str(out_graphml)])
    assert result.exit_code == 0
    assert out_graphml.exists()
    assert "nodes" in result.stdout

def test_cli_kg_query(tmp_path: Path) -> None:
    nodes_csv = tmp_path / "nodes.csv"
    edges_csv = tmp_path / "edges.csv"
    
    pd.DataFrame([
        {"id": "A", "label": "Node A", "type": "type1"},
        {"id": "B", "label": "Node B", "type": "type2"},
    ]).to_csv(nodes_csv, index=False)
    
    pd.DataFrame([
        {"src": "A", "dst": "B", "rel": "connects"},
    ]).to_csv(edges_csv, index=False)
    
    result = runner.invoke(app, ["kg-query", str(nodes_csv), str(edges_csv), "--node", "A"])
    assert result.exit_code == 0
    assert "Neighbors" in result.stdout


