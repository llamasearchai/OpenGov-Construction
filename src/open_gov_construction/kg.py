from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import networkx as nx
import pandas as pd

def build_graph(nodes_csv: Path, edges_csv: Path) -> nx.MultiDiGraph:
    """
    Build a knowledge graph from nodes and edges CSVs.

    nodes: id,label,type
    edges: src,dst,rel
    """
    nodes = pd.read_csv(nodes_csv)
    edges = pd.read_csv(edges_csv)
    for c in ("id", "label", "type"):
        if c not in nodes.columns:
            raise ValueError(f"Missing node column: {c}")
    for c in ("src", "dst", "rel"):
        if c not in edges.columns:
            raise ValueError(f"Missing edge column: {c}")
    G = nx.MultiDiGraph()
    for _, r in nodes.iterrows():
        G.add_node(str(r["id"]), label=str(r["label"]), type=str(r["type"]))
    for _, r in edges.iterrows():
        G.add_edge(str(r["src"]), str(r["dst"]), rel=str(r["rel"]))
    return G

def neighbors_of(G: nx.MultiDiGraph, node_id: str) -> List[str]:
    return list(G.successors(node_id))

def save_graphml(G: nx.MultiDiGraph, path: Path) -> None:
    nx.write_graphml(G, path)

