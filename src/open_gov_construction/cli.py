from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from .states import get_state, list_states
from .schedule import CPMResult, Task, cpm, monte_carlo_duration, read_tasks_csv
from .cost import BABAConfig, screen_baba_dbra
from .media import find_duplicates, scan_images
from .kg import build_graph, neighbors_of, save_graphml

app = typer.Typer(help="OpenGov-Construction: Federal/State construction toolkit (IN, OH, CA).")
console = Console(theme=Theme({"info": "cyan", "error": "red", "success": "green"}))


@app.command("list-states")
def cmd_list_states() -> None:
    profiles = list_states()
    lines = [f"{p.code}: {p.name} (Agencies: {', '.join(p.agencies)})" for p in profiles]
    console.print(Panel("\n".join(lines), title="Supported States"))


@app.command("schedule-cpm")
def cmd_schedule_cpm(
    infile: Path = typer.Argument(..., help="Tasks CSV: task_id,name,duration_days,predecessors[,optimistic_days,likely_days,pessimistic_days]"),
    out_csv: Path = typer.Option(Path("schedule_cpm.csv"), "--out", help="Output CSV with CPM fields."),
) -> None:
    tasks = read_tasks_csv(infile)
    res = cpm(tasks)
    df = pd.DataFrame(
        [
            {
                "task_id": tid,
                "ES": res.es[tid],
                "EF": res.ef[tid],
                "LS": res.ls[tid],
                "LF": res.lf[tid],
                "total_float": res.total_float[tid],
                "critical": abs(res.total_float[tid]) < 1e-9,
            }
            for tid in res.es.keys()
        ]
    ).sort_values("ES")
    df.to_csv(out_csv, index=False)
    console.print(Panel(f"Project duration: {res.project_duration_days:.2f} days\nWrote {out_csv}", title="CPM"))


@app.command("schedule-montecarlo")
def cmd_schedule_mc(
    infile: Path = typer.Argument(..., help="Tasks CSV with optimistic, likely, pessimistic durations."),
    iterations: int = typer.Option(2000, "--iterations", help="Simulation iterations."),
    seed: int = typer.Option(42, "--seed", help="Random seed."),
) -> None:
    tasks = read_tasks_csv(infile)
    p50, p80, p90 = monte_carlo_duration(tasks, iterations=iterations, seed=seed)
    console.print(Panel(f"P50={p50:.1f} d, P80={p80:.1f} d, P90={p90:.1f} d", title="Schedule Risk (Triangular)"))


@app.command("cost-compliance")
def cmd_cost_compliance(
    infile: Path = typer.Argument(..., help="Cost items CSV."),
    out_csv: Path = typer.Option(Path("cost_compliance.csv"), "--out", help="Output CSV with flags."),
    domestic_threshold: float = typer.Option(55.0, "--domestic-threshold", help="Manufactured domestic % threshold."),
) -> None:
    df = screen_baba_dbra(infile, out_csv, baba=BABAConfig(domestic_content_threshold_pct=domestic_threshold))
    n_baba = int(df["flag_baba"].sum()) if "flag_baba" in df else 0
    n_dbra = int(df["flag_dbra"].sum()) if "flag_dbra" in df else 0
    console.print(Panel(f"BABA flags: {n_baba}, DBRA flags: {n_dbra}\nWrote {out_csv}", title="Cost Compliance"))


@app.command("media-scan")
def cmd_media_scan(
    folder: Path = typer.Argument(..., help="Folder containing images."),
    dup_distance: int = typer.Option(5, "--dup-distance", help="Max Hamming distance for duplicates."),
    out_csv: Path = typer.Option(Path("media_inventory.csv"), "--out", help="Output CSV inventory."),
) -> None:
    infos = scan_images(folder)
    import pandas as pd

    df = pd.DataFrame([{"path": i.path, "width": i.width, "height": i.height, "brightness": i.brightness, "phash": i.phash} for i in infos])
    df.to_csv(out_csv, index=False)
    dups = find_duplicates(infos, max_distance=dup_distance)
    dup_lines = [f"{a.path} <-> {b.path} (d={d})" for a, b, d in dups]
    console.print(Panel(f"Scanned {len(infos)} images\nDuplicates: {len(dups)}\n" + "\n".join(dup_lines), title="Media Scan"))


@app.command("kg-build")
def cmd_kg_build(
    nodes_csv: Path = typer.Argument(..., help="Nodes CSV: id,label,type"),
    edges_csv: Path = typer.Argument(..., help="Edges CSV: src,dst,rel"),
    out_graphml: Path = typer.Option(Path("graph.graphml"), "--out", help="Output GraphML path."),
) -> None:
    G = build_graph(nodes_csv, edges_csv)
    save_graphml(G, out_graphml)
    console.print(Panel(f"Graph with {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\nSaved to {out_graphml}", title="KG Build"))


@app.command("kg-query")
def cmd_kg_query(
    nodes_csv: Path = typer.Argument(...),
    edges_csv: Path = typer.Argument(...),
    node_id: str = typer.Option(..., "--node", help="Node ID to query successors."),
) -> None:
    G = build_graph(nodes_csv, edges_csv)
    neigh = neighbors_of(G, node_id)
    console.print(Panel(f"Neighbors of {node_id}: {', '.join(neigh) if neigh else '(none)'}", title="KG Query"))


if __name__ == "__main__":
    app()

