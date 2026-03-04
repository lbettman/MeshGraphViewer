#!/usr/bin/env python3
import json
import sys
from collections import deque
from pathlib import Path

ACTIVE = Path("graph.json")
SMALL  = Path("graph-small.json")
LARGE  = Path("graph-large.json")

PATH_COLOR = "#FFD54A"  # yellow highlight

def load_json(p: Path):
    return json.loads(p.read_text())

def save_active(g):
    tmp = ACTIVE.with_suffix(".tmp")
    tmp.write_text(json.dumps(g, indent=2))
    tmp.replace(ACTIVE)
    ACTIVE.touch()

def clear_colors(g):
    for e in g.get("links", []):
        e.pop("color", None)
    for n in g.get("nodes", []):
        n.pop("color", None)

def undirected_adj(nodes, links):
    ids = {n["id"] for n in nodes if "id" in n}
    adj = {i: set() for i in ids}
    for e in links:
        a, b = e.get("source"), e.get("target")
        if a in ids and b in ids:
            adj[a].add(b)
            adj[b].add(a)
    return adj

def bfs_path(adj, s, t):
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

def highlight_path(g, path):
    edges = set(edge_key(path[i], path[i+1]) for i in range(len(path)-1))
    for e in g.get("links", []):
        a, b = e.get("source"), e.get("target")
        if a is None or b is None:
            continue
        if edge_key(a, b) in edges:
            e["color"] = PATH_COLOR
        else:
            e.pop("color", None)

def cmd_small():
    g = load_json(SMALL)
    clear_colors(g)
    save_active(g)

def cmd_large():
    g = load_json(LARGE)
    clear_colors(g)
    save_active(g)

def cmd_clear():
    g = load_json(ACTIVE)
    clear_colors(g)
    save_active(g)

def cmd_bfs(s, t):
    g = load_json(ACTIVE)
    clear_colors(g)  # start from clean every time
    adj = undirected_adj(g.get("nodes", []), g.get("links", []))
    path = bfs_path(adj, s, t)
    if path and len(path) >= 2:
        highlight_path(g, path)
    save_active(g)

def main(argv):
    if len(argv) < 2:
        print("Usage: mesh_demo.py small|large|clear|bfs <START> <END>", file=sys.stderr)
        return 2
    cmd = argv[1].lower()

    if cmd == "small":
        cmd_small(); return 0
    if cmd == "large":
        cmd_large(); return 0
    if cmd == "clear":
        cmd_clear(); return 0
    if cmd == "bfs" and len(argv) >= 4:
        cmd_bfs(argv[2], argv[3]); return 0

    print("Usage: mesh_demo.py small|large|clear|bfs <START> <END>", file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
