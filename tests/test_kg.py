from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from open_gov_construction.kg import build_graph, neighbors_of, save_graphml

def test_kg_neighbors(tmp_path: Path) -> None:
    nodes = pd.DataFrame(
        [
            {"id": "A", "label": "Contract", "type": "document"},
            {"id": "B", "label": "RFI-1", "type": "record"},
            {"id": "C", "label": "Submittal-1", "type": "record"},
        ]
    )
    edges = pd.DataFrame(
        [
            {"src": "A", "dst": "B", "rel": "references"},
            {"src": "A", "dst": "C", "rel": "contains"},
        ]
    )
    nfile = tmp_path / "nodes.csv"
    efile = tmp_path / "edges.csv"
    nodes.to_csv(nfile, index=False)
    edges.to_csv(efile, index=False)
    G = build_graph(nfile, efile)
    neigh = neighbors_of(G, "A")
    assert set(neigh) == {"B", "C"}

def test_kg_build_graph_missing_node_column(tmp_path: Path) -> None:
    nodes = pd.DataFrame([{"id": "A", "label": "Node A"}])
    edges = pd.DataFrame([{"src": "A", "dst": "B", "rel": "connects"}])
    nfile = tmp_path / "nodes.csv"
    efile = tmp_path / "edges.csv"
    nodes.to_csv(nfile, index=False)
    edges.to_csv(efile, index=False)
    with pytest.raises(ValueError, match="Missing node column"):
        build_graph(nfile, efile)

def test_kg_build_graph_missing_edge_column(tmp_path: Path) -> None:
    nodes = pd.DataFrame([{"id": "A", "label": "Node A", "type": "type1"}])
    edges = pd.DataFrame([{"src": "A", "dst": "B"}])
    nfile = tmp_path / "nodes.csv"
    efile = tmp_path / "edges.csv"
    nodes.to_csv(nfile, index=False)
    edges.to_csv(efile, index=False)
    with pytest.raises(ValueError, match="Missing edge column"):
        build_graph(nfile, efile)

def test_kg_save_graphml(tmp_path: Path) -> None:
    nodes = pd.DataFrame([
        {"id": "A", "label": "Node A", "type": "type1"},
        {"id": "B", "label": "Node B", "type": "type2"},
    ])
    edges = pd.DataFrame([
        {"src": "A", "dst": "B", "rel": "connects"},
    ])
    nfile = tmp_path / "nodes.csv"
    efile = tmp_path / "edges.csv"
    nodes.to_csv(nfile, index=False)
    edges.to_csv(efile, index=False)
    G = build_graph(nfile, efile)
    
    outfile = tmp_path / "graph.graphml"
    save_graphml(G, outfile)
    assert outfile.exists()

