#!/usr/bin/env python3
import json
import sys
import time
from collections import deque
from pathlib import Path

GRAPH_PATH = Path("graph.json")
PACKET_ID = "pkt"

TICK_SECONDS = 0.25

def load_graph():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(f"{GRAPH_PATH} not found")
    return json.loads(GRAPH_PATH.read_text())

def save_graph_atomic(g):
    tmp = GRAPH_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(g, indent=2))
    tmp.replace(GRAPH_PATH)
    # bump timestamp (helps watchers)
    GRAPH_PATH.touch()

def normalize_graph(g):
    g.setdefault("nodes", [])
    g.setdefault("links", [])
    return g

def build_adj(nodes, links):
    ids = {n.get("id") for n in nodes if "id" in n}
    adj = {i: set() for i in ids}
    for e in links:
        a = e.get("source")
        b = e.get("target")
        if a in ids and b in ids:
            # treat as undirected mesh
            adj[a].add(b)
            adj[b].add(a)
    return adj

def bfs_path(adj, src, dst):
    if src not in adj or dst not in adj:
        return None
    q = deque([src])
    prev = {src: None}
    while q:
        u = q.popleft()
        if u == dst:
            break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    if dst not in prev:
        return None
    # reconstruct
    path = []
    cur = dst
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

def remove_packet(g):
    g["nodes"] = [n for n in g["nodes"] if n.get("id") != PACKET_ID]
    g["links"] = [
        e for e in g["links"]
        if e.get("source") != PACKET_ID and e.get("target") != PACKET_ID
    ]

def place_packet(g, at_node_id):
    # add a visible "packet" node linked to current hop
    g["nodes"].append({"id": PACKET_ID, "name": "PACKET"})
    g["links"].append({"source": PACKET_ID, "target": at_node_id})

def cmd_route(src, dst):
    g0 = normalize_graph(load_graph())

    # Always start from a "clean" graph without any previous packet
    remove_packet(g0)

    nodes = g0["nodes"]
    links = g0["links"]
    adj = build_adj(nodes, links)
    path = bfs_path(adj, src, dst)

    if not path:
        # No route: still write clean graph (packet removed) and exit
        save_graph_atomic(g0)
        return

    # Animate hop-by-hop along the BFS path
    for hop in path:
        g = json.loads(json.dumps(g0))  # deep-ish copy
        remove_packet(g)
        place_packet(g, hop)
        save_graph_atomic(g)
        time.sleep(TICK_SECONDS)

    # Leave the packet at destination briefly, then remove it
    time.sleep(TICK_SECONDS)
    remove_packet(g0)
    save_graph_atomic(g0)

def cmd_set_speed(seconds_str):
    global TICK_SECONDS
    TICK_SECONDS = max(0.05, float(seconds_str))

def cmd_help():
    print(
        "mesh_control.py commands:\n"
        "  route <SRC> <DST>      Animate a packet along BFS path\n"
        "  speed <SECONDS>        Set animation tick (e.g. 0.15)\n"
        "Examples:\n"
        "  route 1 25\n"
        "  speed 0.15\n"
    )

def main(argv):
    if len(argv) < 2:
        cmd_help()
        return 0

    cmd = argv[1].strip().lower()

    if cmd == "route" and len(argv) >= 4:
        cmd_route(argv[2], argv[3])
        return 0

    if cmd == "speed" and len(argv) >= 3:
        cmd_set_speed(argv[2])
        return 0

    cmd_help()
    return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv))