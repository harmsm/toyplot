# Copyright 2014, Sandia Corporation. Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains certain
# rights in this software.

"""Provides spatial indexing algorithms.
"""

from __future__ import division

import toyplot

class QuadTree(object):

    class BBox(object):
        def __init__(self, xmin, xmax, ymin, ymax):
            self.xmin = min(xmin, xmax)
            self.xmax = max(xmin, xmax)
            self.ymin = min(ymin, ymax)
            self.ymax = max(ymin, ymax)

        def __repr__(self):
            return "<toyplot.spatial.QuadTree.BBox %r %r %r %r>" % (self.xmin, self.xmax, self.ymin, self.ymax)

        def contains(self, other):
            if other.xmin < self.xmin:
                return False
            if other.xmax > self.xmax:
                return False
            if other.ymin < self.ymin:
                return False
            if other.ymax > self.ymax:
                return False
            return True

        def intersects(self, other):
            return other.xmax >= self.xmin and other.xmin <= self.xmax and other.ymax >= self.ymin and other.ymin <= self.xmax

    class Node(object):
        def __init__(self, bbox):
            self.bbox = bbox
            self.nodes = []
            self.leaves = []

        def node_count(self):
            count = len(self.nodes)
            for node in self.nodes:
                count += node.node_count()
            return count

        def item_count(self):
            count = len(self.leaves)
            for node in self.nodes:
                count += node.item_count()
            return count

        def _insert(self, leaf, max_leaves=10):
            if self.nodes:
                self._child_insert(leaf, max_leaves)
            else:
                self.leaves.append(leaf)
                if len(self.leaves) > max_leaves:
                    bbox = self.bbox

                    center = (
                        (bbox.xmin + bbox.xmax) * 0.5,
                        (bbox.ymin + bbox.ymax) * 0.5,
                        )

                    self.nodes = [
                        QuadTree.Node(QuadTree.BBox(bbox.xmin, center[0], bbox.ymin, center[1])),
                        QuadTree.Node(QuadTree.BBox(bbox.xmin, center[0], center[1], bbox.ymax)),
                        QuadTree.Node(QuadTree.BBox(center[0], bbox.xmax, bbox.ymin, center[1])),
                        QuadTree.Node(QuadTree.BBox(center[0], bbox.xmax, center[1], bbox.ymax)),
                    ]

                    leaves = self.leaves
                    self.leaves = []
                    for leaf in leaves:
                        self._child_insert(leaf, max_leaves)

        def _child_insert(self, leaf, max_leaves):
            for node in self.nodes:
                if node.bbox.contains(leaf.bbox):
                    node._insert(leaf, max_leaves)
                    return

            self.leaves.append(leaf)

        def _intersect(self, bbox, results, depth=0):
            for node in self.nodes:
                if bbox.intersects(node.bbox):
                    toyplot.log.debug("intersect %s", depth+1)
                    node._intersect(bbox, results, depth+1)
            for leaf in self.leaves:
                if bbox.intersects(leaf.bbox):
                    results.add(leaf.item)


    class Leaf(object):
        def __init__(self, item, bbox):
            self.item = item
            self.bbox = bbox

    def __init__(self, bbox, max_leaves=10):
        self.root = QuadTree.Node(QuadTree.BBox(*bbox))
        self.max_leaves = max_leaves

    def __repr__(self):
        return "<toyplot.spatial.QuadTree with %r nodes, %r items>" % (self.node_count(), self.item_count())

    def node_count(self):
        return self.root.node_count()

    def item_count(self):
        return self.root.item_count()

    def insert(self, item, bbox=None, point=None):
        if bbox is not None:
            bbox = QuadTree.BBox(*bbox)
        elif point is not None:
            bbox = QuadTree.BBox(point[0], point[0], point[1], point[1])
        else:
            raise ValueError("Must specify bbox or point.")

        self.root._insert(QuadTree.Leaf(item, bbox), max_leaves=self.max_leaves)

    def intersect(self, bbox):
        results = set()
        self.root._intersect(QuadTree.BBox(*bbox), results)
        return results

