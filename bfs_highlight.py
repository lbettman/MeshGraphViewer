#!/usr/bin/env python3
import json
import sys
from collections import deque
from pathlib import Path

GRAPH = Path("graph.json")
PATH_COLOR = "#FFD54A"   # yellow-ish
DEFAULT_LINK_COLOR = None  # remove explicit color to fall back to default

def load():
    return json.loads(GRAPH.read_text())

def save(g):
    tmp = GRAPH.with_suffix(".tmp")
    tmp.write_text(json.dumps(g, indent=2))
    tmp.replace(GRAPH)
    GRAPH.touch()

def undirected_adj(nodes, links):
    ids = {n["id"] for n in nodes}
    adj = {i: set() for i in ids}
    for e in links:
        a, b = e.get("source"), e.get("target")
        if a in ids and b in ids:
            adj[a].add(b)
            adj[b].add(a)
    return adj

def bfs(adj, s, t):
    if s not in adj or t not in adj:
        return None
    q = deque([s])
    prev = {s: None}
    while q:
        u = q.popleft()
        if u == t:
            break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    if t not in prev:
        return None
    path = []
    cur = t
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

def edge_key(a, b):
    return tuple(sorted((str(a), str(b))))

def clear_link_colors(g):
    for e in g.get("links", []):
        if "color" in e and DEFAULT_LINK_COLOR is None:
            e.pop("color", None)

def highlight_path(g, path):
    # Build set of undirected edges in the path
    path_edges = set()
    for i in range(len(path) - 1):
        path_edges.add(edge_key(path[i], path[i+1]))

    # Apply color to edges that are in the BFS path
    for e in g.get("links", []):
        a, b = e.get("source"), e.get("target")
        if a is None or b is None:
            continue
        if edge_key(a, b) in path_edges:
            e["color"] = PATH_COLOR
        else:
            # remove explicit color so default styling applies
            e.pop("color", None)

def main():
    if len(sys.argv) < 3:
        print("Usage: bfs_highlight.py <START> <END>", file=sys.stderr)
        return 2
    start, end = sys.argv[1], sys.argv[2]

    g = load()
    nodes = g.get("nodes", [])
    links = g.get("links", [])
    adj = undirected_adj(nodes, links)
    path = bfs(adj, start, end)

    # Always clear existing highlights
    clear_link_colors(g)

    if not path or len(path) < 2:
        # no path found; just write cleared version
        save(g)
        return 0

    highlight_path(g, path)
    save(g)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
