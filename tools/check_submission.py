#!/usr/bin/env python3
"""Exploratory schema, colouring and optional layer planarity checks.
Never claims chi(G)=k: independently checked non-(k-1)-colourability is absent.
"""
import argparse
import json
import sys


def validate(data, check_planarity=False):
    expected = {"num_vertices", "edges_part1", "edges_part2", "coloring", "chromatic_number"}
    if not isinstance(data, dict) or not expected.issubset(data):
        raise ValueError("Missing required fields")
    n, k = data["num_vertices"], data["chromatic_number"]
    if type(n) is not int or n <= 0 or type(k) is not int or not (1 <= k <= n):
        raise ValueError("Invalid n or k")
    color = data["coloring"]
    if not isinstance(color, list) or len(color) != n or any(type(c) is not int for c in color):
        raise ValueError("Bad colouring list")
    if len(set(color)) != k:
        raise ValueError("Colouring must use exactly k distinct colours")
    layers = []
    union = set()
    for part in ("edges_part1", "edges_part2"):
        values = data[part]
        if not isinstance(values, list):
            raise ValueError("Edges must be lists")
        layer = []
        seen = set()
        for edge in values:
            if (not isinstance(edge, list) or len(edge) != 2
                    or any(type(x) is not int or x < 0 or x >= n for x in edge)):
                raise ValueError("Invalid edge")
            u, v = edge
            if u == v:
                raise ValueError("Loop")
            e = (min(u, v), max(u, v))
            if e in seen or e in union:
                raise ValueError("Duplicate/overlapping edge")
            if color[u] == color[v]:
                raise ValueError("Improper colouring")
            seen.add(e)
            layer.append(e)
        union.update(seen)
        layers.append(layer)
    if check_planarity:
        try:
            import networkx as nx
        except ImportError as exc:
            raise RuntimeError("NetworkX required for exploratory planarity check") from exc
        for layer in layers:
            graph = nx.Graph()
            graph.add_nodes_from(range(n))
            graph.add_edges_from(layer)
            if not nx.check_planarity(graph)[0]:
                raise ValueError("Nonplanar layer")
    return {"vertices": n, "edges": len(union), "proper_colouring_uses": k,
            "layer_planarity_checked": bool(check_planarity),
            "chromatic_lower_bound_certified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--check-planarity", action="store_true")
    args = parser.parse_args()
    with open(args.path, encoding="utf8") as handle:
        data = json.load(handle)
    result = validate(data, args.check_planarity)
    print(json.dumps(result, indent=2))
    print("NOT A CHROMATIC-NUMBER CERTIFICATE", file=sys.stderr)


if __name__ == "__main__":
    main()
