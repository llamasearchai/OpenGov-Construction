from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from open_gov_construction.schedule import cpm, read_tasks_csv, monte_carlo_duration, Task

def test_cpm_chain(tmp_path: Path) -> None:
    # A -> B -> C with durations 5, 3, 2 => project 10 days; all critical
    df = pd.DataFrame(
        [
            {"task_id": "A", "name": "A", "duration_days": 5.0, "predecessors": ""},
            {"task_id": "B", "name": "B", "duration_days": 3.0, "predecessors": "A"},
            {"task_id": "C", "name": "C", "duration_days": 2.0, "predecessors": "B"},
        ]
    )
    infile = tmp_path / "tasks.csv"
    df.to_csv(infile, index=False)
    res = cpm(read_tasks_csv(infile))
    assert abs(res.project_duration_days - 10.0) < 1e-9
    assert set(res.critical_path) == {"A", "B", "C"}

def test_cpm_with_cycle_detection(tmp_path: Path) -> None:
    # Create a cycle: A -> B -> C -> A
    df = pd.DataFrame(
        [
            {"task_id": "A", "name": "A", "duration_days": 5.0, "predecessors": "C"},
            {"task_id": "B", "name": "B", "duration_days": 3.0, "predecessors": "A"},
            {"task_id": "C", "name": "C", "duration_days": 2.0, "predecessors": "B"},
        ]
    )
    infile = tmp_path / "tasks_cycle.csv"
    df.to_csv(infile, index=False)
    tasks = read_tasks_csv(infile)
    with pytest.raises(ValueError, match="Cycle detected"):
        cpm(tasks)

def test_read_tasks_csv_missing_column(tmp_path: Path) -> None:
    df = pd.DataFrame([
        {"task_id": "A", "name": "A", "duration_days": 5.0},
    ])
    infile = tmp_path / "tasks_bad.csv"
    df.to_csv(infile, index=False)
    with pytest.raises(ValueError, match="Missing required column"):
        read_tasks_csv(infile)

def test_monte_carlo_deterministic(tmp_path: Path) -> None:
    df = pd.DataFrame(
        [
            {"task_id": "A", "name": "A", "duration_days": 5.0, "predecessors": "", "optimistic_days": 4.0, "likely_days": 5.0, "pessimistic_days": 7.0},
            {"task_id": "B", "name": "B", "duration_days": 3.0, "predecessors": "A", "optimistic_days": 2.0, "likely_days": 3.0, "pessimistic_days": 6.0},
        ]
    )
    infile = tmp_path / "tasks_mc.csv"
    df.to_csv(infile, index=False)
    tasks = read_tasks_csv(infile)
    p50_1, p80_1, p90_1 = monte_carlo_duration(tasks, iterations=1000, seed=123)
    p50_2, p80_2, p90_2 = monte_carlo_duration(tasks, iterations=1000, seed=123)
    assert (p50_1, p80_1, p90_1) == (p50_2, p80_2, p90_2)

def test_monte_carlo_no_uncertainty(tmp_path: Path) -> None:
    # Test fallback to fixed duration when uncertainty not provided
    df = pd.DataFrame([
        {"task_id": "A", "name": "A", "duration_days": 5.0, "predecessors": ""},
    ])
    infile = tmp_path / "tasks_fixed.csv"
    df.to_csv(infile, index=False)
    tasks = read_tasks_csv(infile)
    p50, p80, p90 = monte_carlo_duration(tasks, iterations=100, seed=42)
    # With no uncertainty, all percentiles should be equal to duration
    assert abs(p50 - 5.0) < 0.01
    assert abs(p80 - 5.0) < 0.01
    assert abs(p90 - 5.0) < 0.01

