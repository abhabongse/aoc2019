from __future__ import annotations

import collections
import heapq
import itertools
import math
import os
import string
import time
from collections.abc import Iterator, Mapping, Set
from typing import NamedTuple, TypeVar

import more_itertools
from tqdm import tqdm

from mysolution.geometry import Vec

T = TypeVar('T')

LOCK_KEY_PAIRS = {c.upper(): c for c in string.ascii_lowercase}
ORTHOGONAL_STEPS = [Vec(1, 0), Vec(0, 1), Vec(-1, 0), Vec(0, -1)]


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    grid = read_input_file(input_file)

    # Part 1
    p1_answer = shortest_trip_to_keys(grid)
    print(p1_answer)
    time.sleep(1)

    # Part 2
    p2_answer = shortest_trip_to_keys(modify_grid(grid))
    print(p2_answer)


class Edge(NamedTuple):
    succ: str
    length: int


class SuperNode(NamedTuple):
    robots: tuple[Vec, ...]
    visited: frozenset[str]


def shortest_trip_to_keys(grid: Mapping[Vec, str]) -> int:
    """
    Computes the shortest distance of a trip from the starting positions
    to gather all keys (represented by node labels in lowercase).
    """
    available_keys = {char: pos for pos, char in grid.items() if char in string.ascii_lowercase}
    entrances = tuple(pos for pos, char in grid.items() if char == '@')

    source = SuperNode(entrances, frozenset())
    distances = {}
    prelim_distances = {source: 0}
    queue = [(0, source)]

    with tqdm(desc="Node", total=1) as pbar:
        while queue:
            dist, node = heapq.heappop(queue)
            pbar.update(1)
            if node in distances:
                continue
            distances[node] = dist
            if available_keys.keys() <= node.visited:
                return dist
            for i, r in enumerate(node.robots):
                for e in find_edges(grid, r, node.visited):
                    new_dist = dist + e.length
                    new_robots = tuple_replace(node.robots, i, available_keys[e.succ])
                    new_node = SuperNode(new_robots, node.visited | {e.succ})
                    if new_dist < prelim_distances.get(new_node, math.inf):
                        prelim_distances[new_node] = new_dist
                        heapq.heappush(queue, (new_dist, new_node))
                        pbar.total += 1


def find_edges(grid: Mapping[Vec, str], source: Vec, visited: Set[str]) -> Iterator[Edge]:
    """
    Produces a sequence of edges from the given node.
    """
    distances = {source: 0}
    queue = collections.deque([source])
    while queue:
        pos = queue.popleft()
        for step in ORTHOGONAL_STEPS:
            adj_pos = pos + step
            adj_char = grid.get(adj_pos, '#')
            if adj_char == '#' or adj_pos in distances:
                continue
            distances[adj_pos] = distances[pos] + 1
            if adj_char in string.ascii_lowercase:
                yield Edge(adj_char, distances[adj_pos])
            if grid[adj_pos] in ('.', '@') or LOCK_KEY_PAIRS.get(grid[adj_pos]) in visited:
                queue.append(adj_pos)


def modify_grid(grid: Mapping[Vec, str]) -> dict[Vec, str]:
    """
    Modify the grid by replacing one entrance with four which are diagonally adjacent.
    """
    center = more_itertools.one(pos for pos, char in grid.items() if char == '@')
    grid = dict(grid)
    grid[center] = '#'
    for step in ORTHOGONAL_STEPS:
        grid[center + step] = '#'
    for dx, dy in itertools.product([-1, 1], [-1, 1]):
        grid[center + Vec(dx, dy)] = '@'
    return grid


def tuple_replace(data: tuple[T, ...], index: int, value: T) -> tuple[T, ...]:
    """
    Duplicates the tuple but replacing the new value at the given index.
    """
    if not 0 <= index < len(data):
        raise IndexError
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
