from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Task:
    task_id: str
    name: str
    duration_days: float
    predecessors: tuple[str, ...]
    optimistic_days: Optional[float] = None
    likely_days: Optional[float] = None
    pessimistic_days: Optional[float] = None

@dataclass(frozen=True)
class CPMResult:
    project_duration_days: float
    es: Dict[str, float]
    ef: Dict[str, float]
    ls: Dict[str, float]
    lf: Dict[str, float]
    total_float: Dict[str, float]
    critical_path: List[str]

def read_tasks_csv(path: Path) -> List[Task]:
    df = pd.read_csv(path)
    required = ["task_id", "name", "duration_days", "predecessors"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")
    tasks: List[Task] = []
    for _, r in df.iterrows():
        preds = tuple([p.strip() for p in str(r["predecessors"]).split(",") if p.strip()]) if pd.notna(r["predecessors"]) else tuple()
        tasks.append(
            Task(
                task_id=str(r["task_id"]),
                name=str(r["name"]),
                duration_days=float(r["duration_days"]),
                predecessors=preds,
                optimistic_days=float(r["optimistic_days"]) if "optimistic_days" in df.columns and pd.notna(r["optimistic_days"]) else None,
                likely_days=float(r["likely_days"]) if "likely_days" in df.columns and pd.notna(r["likely_days"]) else None,
                pessimistic_days=float(r["pessimistic_days"]) if "pessimistic_days" in df.columns and pd.notna(r["pessimistic_days"]) else None,
            )
        )
    return tasks

def _topo_order(tasks: List[Task]) -> List[str]:
    ids = {t.task_id for t in tasks}
    preds = {t.task_id: set(t.predecessors) for t in tasks}
    # Kahn's algorithm
    ready = [tid for tid in ids if not preds[tid]]
    order: List[str] = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for t in tasks:
            if n in preds[t.task_id]:
                preds[t.task_id].remove(n)
                if not preds[t.task_id]:
                    ready.append(t.task_id)
    if any(preds[tid] for tid in preds):
        raise ValueError("Cycle detected in predecessors; ensure DAG schedule.")
    return order

def cpm(tasks: List[Task]) -> CPMResult:
    by_id = {t.task_id: t for t in tasks}
    order = _topo_order(tasks)
    es: Dict[str, float] = {}
    ef: Dict[str, float] = {}
    for tid in order:
        t = by_id[tid]
        es[tid] = max([ef[p] for p in t.predecessors], default=0.0)
        ef[tid] = es[tid] + t.duration_days
    proj_duration = max(ef.values()) if ef else 0.0
    # Backward pass
    ls: Dict[str, float] = {}
    lf: Dict[str, float] = {}
    for tid in reversed(order):
        t = by_id[tid]
        succ = [s.task_id for s in tasks if tid in s.predecessors]
        if succ:
            lf[tid] = min([ls[s] for s in succ])
        else:
            lf[tid] = proj_duration
        ls[tid] = lf[tid] - t.duration_days
    tf = {tid: ls[tid] - es[tid] for tid in order}
    critical = [tid for tid in order if abs(tf[tid]) < 1e-9]
    return CPMResult(proj_duration, es, ef, ls, lf, tf, critical)

def monte_carlo_duration(tasks: List[Task], iterations: int = 1000, seed: int = 42) -> Tuple[float, float, float]:
    """
    Return P50, P80, P90 project durations (days) using triangular sampling where provided.
    Fallback to fixed duration if no uncertainty is provided.
    """
    rng = np.random.default_rng(seed)
    by_id = {t.task_id: t for t in tasks}
    order = _topo_order(tasks)
    durations = np.zeros(len(order), dtype=float)
    idx_map = {tid: i for i, tid in enumerate(order)}
    samples = np.zeros(iterations, dtype=float)
    for it in range(iterations):
        # Sample durations
        for tid in order:
            t = by_id[tid]
            if t.optimistic_days is not None and t.likely_days is not None and t.pessimistic_days is not None:
                durations[idx_map[tid]] = rng.triangular(t.optimistic_days, t.likely_days, t.pessimistic_days)
            else:
                durations[idx_map[tid]] = t.duration_days
        # Forward pass
        es: Dict[str, float] = {}
        ef: Dict[str, float] = {}
        for tid in order:
            t = by_id[tid]
            es[tid] = max([ef[p] for p in t.predecessors], default=0.0)
            ef[tid] = es[tid] + durations[idx_map[tid]]
        samples[it] = max(ef.values()) if ef else 0.0
    p50 = float(np.percentile(samples, 50))
    p80 = float(np.percentile(samples, 80))
    p90 = float(np.percentile(samples, 90))
    return p50, p80, p90

