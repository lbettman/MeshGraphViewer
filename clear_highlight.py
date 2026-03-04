#!/usr/bin/env python3
import json
from pathlib import Path

GRAPH = Path("graph.json")

g = json.loads(GRAPH.read_text())

for e in g.get("links", []):
    e.pop("color", None)
for n in g.get("nodes", []):
    n.pop("color", None)

tmp = GRAPH.with_suffix(".tmp")
tmp.write_text(json.dumps(g, indent=2))
tmp.replace(GRAPH)
GRAPH.touch()
