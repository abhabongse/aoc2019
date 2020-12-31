from __future__ import annotations

import collections
import heapq
import math
import os
import string
from collections.abc import Iterable, Iterator, Mapping, Sequence, Set
from typing import NamedTuple, TypeVar

import more_itertools
from tqdm import tqdm

from mysolution.geometry import Vec

T = TypeVar('T')

LOCK_KEY_PAIRS = {c: c.lower() for c in string.ascii_uppercase}
ORTHOGONAL_STEPS = [Vec(1, 0), Vec(0, 1), Vec(-1, 0), Vec(0, -1)]


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    grid = read_input_file(input_file)

    # Part 1
    graph = build_higher_level_graph(grid)
    p1_answer = find_shortest_trip_to_keys(graph, start=['@'])
    print(p1_answer)

    # Part 2
    graph = build_higher_level_graph(modify_grid(grid))
    p2_answer = find_shortest_trip_to_keys(graph, start=['@0', '@1', '@2', '@3'])
    print(p2_answer)


class Edge(NamedTuple):
    succ: str
    length: int


class SuperNode(NamedTuple):
    robots: tuple[str, ...]
    visited: frozenset[str]


def find_shortest_trip_to_keys(graph: dict[str, Sequence[Edge]], start: Sequence[str]) -> int:
    """
    Computes the shortest distance of a trip to gather all keys
    represented by node labels in lowercase.
    """
    all_keys = frozenset(LOCK_KEY_PAIRS.values()) & graph.keys()
    source = SuperNode(tuple(start), frozenset(start))
    distances = {}
    prelim_distances = {source: 0}
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

            for i, r in enumerate(node.robots):
                for e in filter_edges(graph[r], node.visited):
                    new_dist = dist + e.length
                    new_node = SuperNode(tuple_replace(node.robots, i, e.succ), node.visited | {e.succ})
                    if new_dist < prelim_distances.get(new_node, math.inf):
                        prelim_distances[new_node] = new_dist
                        heapq.heappush(queue, (new_dist, new_node))
                        pbar.total += 1


def filter_edges(edges: Iterable[Edge], visited: Set[str]) -> Iterator[Edge]:
    """
    Filter the given sequence of edges that is allowed to be taken
    given a set of already visited cells.
    """
    for e in edges:
        if e.succ in LOCK_KEY_PAIRS and LOCK_KEY_PAIRS[e.succ] not in visited:
            continue
        yield e


def modify_grid(grid: Mapping[Vec, str]) -> dict[Vec, str]:
    """
    Modify grid, replacing one entrance with four.
    """
    center = more_itertools.one(pos for pos, char in grid.items() if char == '@')
    grid = dict(grid)
    grid[center] = '#'
    grid[center + Vec(1, 0)] = '#'
    grid[center + Vec(0, 1)] = '#'
    grid[center + Vec(-1, 0)] = '#'
    grid[center + Vec(0, -1)] = '#'
    grid[center + Vec(1, 1)] = '@0'
    grid[center + Vec(-1, 1)] = '@1'
    grid[center + Vec(-1, -1)] = '@2'
    grid[center + Vec(1, -1)] = '@3'
    return grid


def build_higher_level_graph(grid: Mapping[Vec, str]) -> dict[str, list[Edge]]:
    """
    Builds a higher-level graph of only content cells from the provided grid.
    """
    graph = {
        char: find_nearby_content_cells(grid, pos)
        for pos, char in grid.items()
        if char not in ('#', '.')
    }
    return graph


def find_nearby_content_cells(grid: Mapping[Vec, str], src_pos: Vec) -> list[Edge]:
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
        if (char := grid[pos]) not in ('#', '.') and dist > 0
    ]


def tuple_replace(data: tuple[T, ...], index: int, value: T) -> tuple[T, ...]:
    return tuple(value if i == index else e for i, e in enumerate(data))


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
