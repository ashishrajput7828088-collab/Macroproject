"""K-D Tree for 2D points (x, y in km).

Build:  split the points at the median, alternating x and y at each level.
Query:  skip whole branches that cannot contain a closer point.
Average search time is about O(log n), versus O(n) for checking every hospital.

Every query accepts an optional `stats` dict. If given, the tree counts its own work:
    stats["nodes"]  = tree nodes visited (a K-D node holds exactly one hospital)
    stats["points"] = hospitals whose distance / position was actually tested
These are REAL counts made while the search runs (used by the comparison panel)."""
import heapq


class KDNode:
    __slots__ = ("point", "item", "axis", "left", "right")

    def __init__(self, point, item, axis):
        self.point, self.item, self.axis = point, item, axis
        self.left = self.right = None


def _count(stats, nodes=0, points=0):
    if stats is not None:
        stats["nodes"] = stats.get("nodes", 0) + nodes
        stats["points"] = stats.get("points", 0) + points


class KDTree:
    def __init__(self, entries):
        """entries = list of ((x, y), item)"""
        self.size = len(entries)
        self.root = self._build(list(entries), 0)

    def _build(self, entries, depth):
        if not entries:
            return None
        axis = depth % 2
        entries.sort(key=lambda e: e[0][axis])
        mid = len(entries) // 2
        node = KDNode(entries[mid][0], entries[mid][1], axis)
        node.left = self._build(entries[:mid], depth + 1)
        node.right = self._build(entries[mid + 1:], depth + 1)
        return node

    def radius_search(self, center, radius, stats=None):
        """Every item within `radius` km of `center`."""
        found = []

        def visit(node):
            if node is None:
                return
            _count(stats, nodes=1, points=1)
            if _dist(node.point, center) <= radius:
                found.append(node.item)
            diff = center[node.axis] - node.point[node.axis]
            near, far = (node.left, node.right) if diff < 0 else (node.right, node.left)
            visit(near)
            if abs(diff) <= radius:      # the circle crosses the splitting line
                visit(far)

        visit(self.root)
        return found

    def range_search(self, rect, stats=None):
        """Rectangle (orthogonal range) query. rect = (x0, y0, x1, y1). Returns the items inside it."""
        x0, y0, x1, y1 = rect
        low, high = (x0, y0), (x1, y1)
        found = []

        def visit(node):
            if node is None:
                return
            _count(stats, nodes=1, points=1)
            p = node.point
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
                found.append(node.item)
            if low[node.axis] <= p[node.axis]:      # the rectangle reaches the left / lower side
                visit(node.left)
            if high[node.axis] >= p[node.axis]:     # the rectangle reaches the right / upper side
                visit(node.right)

        visit(self.root)
        return found

    def nearest(self, center, k=1, stats=None):
        """The k closest items (closest first)."""
        best = []   # max-heap of (-distance, counter, item)
        counter = 0

        def visit(node):
            nonlocal counter
            if node is None:
                return
            _count(stats, nodes=1, points=1)
            d = _dist(node.point, center)
            counter += 1
            if len(best) < k:
                heapq.heappush(best, (-d, counter, node.item))
            elif d < -best[0][0]:
                heapq.heapreplace(best, (-d, counter, node.item))
            diff = center[node.axis] - node.point[node.axis]
            near, far = (node.left, node.right) if diff < 0 else (node.right, node.left)
            visit(near)
            if len(best) < k or abs(diff) < -best[0][0]:
                visit(far)

        visit(self.root)
        return [item for _, _, item in sorted(best, key=lambda b: -b[0])]

    def insert(self, point, item):
        """Dynamic insertion of a single point into the K-D Tree."""
        def _ins(node, depth):
            if node is None:
                self.size += 1
                return KDNode(point, item, depth % 2)
            axis = node.axis
            if point[axis] < node.point[axis]:
                node.left = _ins(node.left, depth + 1)
            else:
                node.right = _ins(node.right, depth + 1)
            return node

        self.root = _ins(self.root, 0)
        return True

    def delete(self, point, item_id=None):
        """Dynamic deletion of a point / item from the K-D Tree."""
        def _find_min(node, target_axis, depth):
            if node is None:
                return None
            axis = depth % 2
            if axis == target_axis:
                if node.left is None:
                    return node
                return _find_min(node.left, target_axis, depth + 1)
            left_min = _find_min(node.left, target_axis, depth + 1)
            right_min = _find_min(node.right, target_axis, depth + 1)
            res = node
            if left_min and left_min.point[target_axis] < res.point[target_axis]:
                res = left_min
            if right_min and right_min.point[target_axis] < res.point[target_axis]:
                res = right_min
            return res

        def _del(node, depth):
            if node is None:
                return None
            axis = depth % 2
            p_match = (abs(node.point[0] - point[0]) < 1e-7 and abs(node.point[1] - point[1]) < 1e-7)
            id_match = (item_id is None) or (node.item == item_id) or (isinstance(node.item, dict) and node.item.get("id") == item_id)

            if p_match and id_match:
                self.size = max(0, self.size - 1)
                if node.right is not None:
                    min_node = _find_min(node.right, axis, depth + 1)
                    node.point = min_node.point
                    node.item = min_node.item
                    node.right = _del(node.right, depth + 1)
                elif node.left is not None:
                    min_node = _find_min(node.left, axis, depth + 1)
                    node.point = min_node.point
                    node.item = min_node.item
                    node.right = _del(node.left, depth + 1)
                    node.left = None
                else:
                    return None
                return node

            if point[axis] < node.point[axis]:
                node.left = _del(node.left, depth + 1)
            else:
                node.right = _del(node.right, depth + 1)
            return node

        self.root = _del(self.root, 0)
        return True


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
