"""Quadtree for 2D points (x, y in km).

Each node covers a square area. When a node holds more than CAPACITY points it
splits into 4 equal quadrants (NW, NE, SW, SE). A search only enters quadrants
that overlap the search circle / search rectangle.

Every query accepts an optional `stats` dict and fills in REAL counts while it runs:
    stats["nodes"]  = quadrant squares visited (inner squares and leaves)
    stats["points"] = hospitals whose distance / position was actually tested"""
import heapq

CAPACITY = 4
MAX_DEPTH = 12   # stops endless splitting if many points share one spot


def _count(stats, nodes=0, points=0):
    if stats is not None:
        stats["nodes"] = stats.get("nodes", 0) + nodes
        stats["points"] = stats.get("points", 0) + points


class QuadNode:
    def __init__(self, x0, y0, x1, y1, depth=0):
        self.bounds = (x0, y0, x1, y1)
        self.depth = depth
        self.points = []      # list of ((x, y), item)
        self.children = None  # 4 QuadNodes after splitting

    def insert(self, point, item):
        x0, y0, x1, y1 = self.bounds
        if not (x0 <= point[0] <= x1 and y0 <= point[1] <= y1):
            return False
        if self.children is None:
            if len(self.points) < CAPACITY or self.depth >= MAX_DEPTH:
                self.points.append((point, item))
                return True
            self._split()
        return any(c.insert(point, item) for c in self.children)

    def _split(self):
        x0, y0, x1, y1 = self.bounds
        mx, my, d = (x0 + x1) / 2, (y0 + y1) / 2, self.depth + 1
        self.children = [QuadNode(x0, my, mx, y1, d), QuadNode(mx, my, x1, y1, d),
                         QuadNode(x0, y0, mx, my, d), QuadNode(mx, y0, x1, my, d)]
        old, self.points = self.points, []
        for p, item in old:
            any(c.insert(p, item) for c in self.children)

    def box_distance(self, c):
        """Distance from point c to the nearest edge of this node's square (0 if inside)."""
        x0, y0, x1, y1 = self.bounds
        dx = max(x0 - c[0], 0, c[0] - x1)
        dy = max(y0 - c[1], 0, c[1] - y1)
        return (dx * dx + dy * dy) ** 0.5

    def overlaps(self, rect):
        x0, y0, x1, y1 = self.bounds
        return not (rect[2] < x0 or rect[0] > x1 or rect[3] < y0 or rect[1] > y1)

    def delete(self, point, item_id=None):
        x0, y0, x1, y1 = self.bounds
        if not (x0 <= point[0] <= x1 and y0 <= point[1] <= y1):
            return False
        if self.children is None:
            initial_len = len(self.points)
            self.points = [
                (p, item) for p, item in self.points
                if not (abs(p[0] - point[0]) < 1e-7 and abs(p[1] - point[1]) < 1e-7 and (item_id is None or item == item_id or (isinstance(item, dict) and item.get("id") == item_id)))
            ]
            return len(self.points) < initial_len
        deleted = any(c.delete(point, item_id) for c in self.children)
        if deleted:
            all_pts = []
            for c in self.children:
                if c.children is not None:
                    return deleted
                all_pts.extend(c.points)
            if len(all_pts) <= CAPACITY:
                self.points = all_pts
                self.children = None
        return deleted


class Quadtree:
    def __init__(self, entries):
        """entries = list of ((x, y), item)"""
        entries = list(entries)
        self.size = len(entries)
        xs = [e[0][0] for e in entries] or [0]
        ys = [e[0][1] for e in entries] or [0]
        pad = 0.001
        self.root = QuadNode(min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
        for p, item in entries:
            self.root.insert(p, item)

    def get_all_entries(self):
        res = []
        def walk(node):
            if node is None:
                return
            res.extend(node.points)
            if node.children:
                for c in node.children:
                    walk(c)
        walk(self.root)
        return res

    def insert(self, point, item):
        self.size += 1
        if not (self.root.bounds[0] <= point[0] <= self.root.bounds[2] and self.root.bounds[1] <= point[1] <= self.root.bounds[3]):
            x0 = min(self.root.bounds[0], point[0] - 1.0)
            y0 = min(self.root.bounds[1], point[1] - 1.0)
            x1 = max(self.root.bounds[2], point[0] + 1.0)
            y1 = max(self.root.bounds[3], point[1] + 1.0)
            all_entries = self.get_all_entries()
            all_entries.append((point, item))
            self.root = QuadNode(x0, y0, x1, y1)
            new_tree = Quadtree(all_entries)
            self.root = new_tree.root
            return True
        return self.root.insert(point, item)

    def delete(self, point, item_id=None):
        deleted = self.root.delete(point, item_id)
        if deleted:
            self.size = max(0, self.size - 1)
        return deleted

    def radius_search(self, center, radius, stats=None):
        found = []

        def visit(node):
            _count(stats, nodes=1)
            if node.box_distance(center) > radius:
                return                      # whole square is too far away
            for p, item in node.points:
                _count(stats, points=1)
                if ((p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2) ** 0.5 <= radius:
                    found.append(item)
            for child in node.children or []:
                visit(child)

        visit(self.root)
        return found

    def range_search(self, rect, stats=None):
        """Rectangle query. rect = (x0, y0, x1, y1). Only squares that overlap the rectangle are opened."""
        x0, y0, x1, y1 = rect
        found = []

        def visit(node):
            _count(stats, nodes=1)
            if not node.overlaps(rect):
                return
            for p, item in node.points:
                _count(stats, points=1)
                if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
                    found.append(item)
            for child in node.children or []:
                visit(child)

        visit(self.root)
        return found

    def nearest(self, center, k=1, stats=None):
        """Best-first search: always open the closest unopened square next."""
        results = []
        counter = 0
        queue = [(0.0, counter, self.root)]
        while queue and len(results) < k:
            _, _, node = heapq.heappop(queue)
            if isinstance(node, QuadNode):
                _count(stats, nodes=1)
                for child in node.children or []:
                    counter += 1
                    heapq.heappush(queue, (child.box_distance(center), counter, child))
                for p, item in node.points:
                    counter += 1
                    _count(stats, points=1)
                    d = ((p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2) ** 0.5
                    heapq.heappush(queue, (d, counter, ("item", item)))
            else:
                results.append(node[1])   # a hospital record popped off the queue
        return results
