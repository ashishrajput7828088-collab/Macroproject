"""Checks that the K-D Tree and Quadtree give the SAME answers as checking every hospital.
Run:  python test_algorithms.py        (no Flask needed)"""
import json, random
from pathlib import Path
from geo import to_xy_km
from kdtree import KDTree
from quadtree import Quadtree

hospitals = json.loads((Path(__file__).parent / "data" / "hospitals.json").read_text())
ref = sum(h["lat"] for h in hospitals) / len(hospitals)
entries = [(to_xy_km(h["lat"], h["lng"], ref), h["id"]) for h in hospitals]
trees = {"kdtree": KDTree(entries), "quadtree": Quadtree(entries)}
random.seed(1)
bad = 0
for _ in range(300):
    lat, lng = 26.2183 + random.uniform(-.1, .1), 78.1828 + random.uniform(-.1, .1)
    c = to_xy_km(lat, lng, ref)
    dist = {h["id"]: ((to_xy_km(h["lat"], h["lng"], ref)[0] - c[0]) ** 2 + (to_xy_km(h["lat"], h["lng"], ref)[1] - c[1]) ** 2) ** .5 for h in hospitals}
    r, k = random.uniform(1, 12), random.randint(1, 6)
    for name, t in trees.items():
        if sorted(t.radius_search(c, r)) != sorted(i for i, d in dist.items() if d <= r):
            bad += 1; print("radius mismatch", name)
        if t.nearest(c, k) != sorted(dist, key=dist.get)[:k]:
            bad += 1; print("nearest mismatch", name)

# Rectangle (range) queries + the counters used by the comparison panel
for _ in range(300):
    x0, y0 = to_xy_km(26.2183 + random.uniform(-.08, .05), 78.1828 + random.uniform(-.08, .05), ref)
    rect = (x0, y0, x0 + random.uniform(.5, 9), y0 + random.uniform(.5, 9))
    expected = sorted(h["id"] for h in hospitals
                      if rect[0] <= to_xy_km(h["lat"], h["lng"], ref)[0] <= rect[2] and rect[1] <= to_xy_km(h["lat"], h["lng"], ref)[1] <= rect[3])
    for name, t in trees.items():
        stats = {}
        if sorted(t.range_search(rect, stats)) != expected:
            bad += 1; print("range mismatch", name)
        if stats["nodes"] < 1 or stats["points"] < 0:
            bad += 1; print("stats missing", name)

# Test dynamic insert & delete
test_pt = (12.345, 67.890)
for name, t in trees.items():
    init_size = t.size
    t.insert(test_pt, 99999)
    if t.size != init_size + 1:
        bad += 1; print("insert size mismatch", name)
    # verify it is found
    nearest_item = t.nearest(test_pt, 1)
    if nearest_item != [99999]:
        bad += 1; print("insert find mismatch", name)
    # delete it
    t.delete(test_pt, 99999)
    if t.size != init_size:
        bad += 1; print("delete size mismatch", name)

print("ALL TESTS PASSED" if not bad else f"{bad} problems found")