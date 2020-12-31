from __future__ import annotations

import collections
import heapq
import os
import string
from collections.abc import Iterable, Iterator, Sequence
from pprint import pprint
from typing import NamedTuple

from tqdm import tqdm

from mysolution.geometry import Vec

DOOR_CELLS = string.ascii_uppercase
KEY_CELLS = string.ascii_lowercase
CONTENT_CELLS = f'@{DOOR_CELLS}{KEY_CELLS}'
ORTHOGONAL_STEPS = [Vec(1, 0), Vec(0, 1), Vec(-1, 0), Vec(0, -1)]


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    grid = read_input_file(input_file)

    # Part 1
    graph = build_higher_level_graph(grid)
    pprint(graph)
    p1_answer = find_shortest_trip_to_keys(graph)
    print(p1_answer)

    # Part 2
    p2_answer = ...
    print(p2_answer)


class Edge(NamedTuple):
    to_node: str
    dist: int


class StateNode(NamedTuple):
    recent: str
    visited: frozenset[str]


def find_shortest_trip_to_keys(graph: dict[str, Sequence[Edge]]) -> int:
    """
    Computes the shortest distance of a trip to gather all keys
    represented by node labels in lowercase.
    """
    all_keys = frozenset(KEY_CELLS) & graph.keys()
    source = StateNode('@', frozenset(['@']))
    distances = {}
    queue = [(0, source)]

    with tqdm(desc="Node States", total=1) as pbar:
        while queue:
            dist, node = heapq.heappop(queue)
            pbar.update(1)
            if node in distances:
                continue
            distances[node] = dist
            if all_keys <= node.visited:
                return dist

            for e in filter_edges(node, graph[node.recent]):
                new_dist = dist + e.dist
                new_node = StateNode(e.to_node, node.visited | {e.to_node})
                if new_node not in distances:
                    # The above check is optional but helps with performance optimization
                    heapq.heappush(queue, (new_dist, new_node))
                    pbar.total += 1


def filter_edges(node: StateNode, edges: Iterable[Edge]) -> Iterator[Edge]:
    """
    Filters edges that could be taken given the current state node.
    """
    for e in edges:
        if e.to_node in DOOR_CELLS and e.to_node.lower() not in node.visited:
            continue
        yield e


def build_higher_level_graph(grid: dict[Vec, str]) -> dict[str, list[Edge]]:
    """
    Builds a higher-level graph of only content cells from the provided grid.
    """
    graph = {
        char: find_nearby_content_cells(grid, pos)
        for pos, char in grid.items()
        if char in CONTENT_CELLS
    }
    return graph


def find_nearby_content_cells(grid: dict[Vec, str], src_pos: Vec) -> list[Edge]:
    """
    Uses breadth-first search (BFS) algorithm to find the shortest distances
    from the given source node to other significant nodes (excl '#' and '.')
    which are not blocked by other signification nodes in their way.
    """
    distances = {src_pos: 0}
    queue = collections.deque([src_pos])
    while queue:
        pos = queue.popleft()
        for step in ORTHOGONAL_STEPS:
            adj_pos = pos + step
            if adj_pos in distances or grid.get(adj_pos, '#') == '#':
                continue
            distances[adj_pos] = distances[pos] + 1
            if grid[adj_pos] == '.':
                queue.append(adj_pos)
    return [
        Edge(char, dist)
        for pos, dist in distances.items()
        if (char := grid[pos]) in CONTENT_CELLS and dist > 0
    ]


def read_input_file(filename: str) -> dict[Vec, str]:
    """
    Extracts a top view underground vault grid.
    """
    with open(filename) as fobj:
        grid = {
            Vec(col, row): char
            for row, line in enumerate(fobj)
            for col, char in enumerate(line.strip())
        }
    return grid


if __name__ == '__main__':
    main()
