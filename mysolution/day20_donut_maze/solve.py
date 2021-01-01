from __future__ import annotations

import collections
import os
import string
from dataclasses import InitVar, dataclass, field
from typing import TypeVar

import more_itertools

from mysolution.geometry import Vec

T = TypeVar('T')

ORTHOGONAL_STEPS = [Vec(1, 0), Vec(0, 1), Vec(-1, 0), Vec(0, -1)]


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    graph = read_input_file(input_file)

    # Part 1
    p1_answer = graph.shortest_distance()
    print(p1_answer)

    # Part 2
    p2_answer = ...
    print(p2_answer)


@dataclass
class Graph:
    grid: InitVar[dict[Vec, str]]
    src_pos: Vec = field(init=False)
    dest_pos: Vec = field(init=False)
    adjlist: collections.defaultdict[Vec, list[Vec]] = field(init=False)

    def __post_init__(self, grid: dict[Vec, str]):
        self.adjlist = collections.defaultdict(list)
        self._gather_orthogonal_edges(grid)
        self._gather_portal_edges(grid)

    def _gather_orthogonal_edges(self, grid: dict[Vec, str]):
        for pos, char in grid.items():
            if char != '.':
                continue
            for step in ORTHOGONAL_STEPS:
                if grid.get(pos + step, '#') != '.':
                    continue
                self.adjlist[pos].append(pos + step)

    def _gather_portal_edges(self, grid: dict[Vec, str]):
        portals = collections.defaultdict(list)
        for pos, char in grid.items():
            if char != '.':
                continue
            for step in ORTHOGONAL_STEPS:
                if grid.get(pos + step, '#') not in string.ascii_uppercase:
                    continue
                fst_pos, snd_pos = sorted([pos + step, pos + step * 2])
                word = grid[fst_pos] + grid[snd_pos]
                portals[word].append(pos)

        self.src_pos = more_itertools.one(portals.pop('AA'))
        self.dest_pos = more_itertools.one(portals.pop('ZZ'))
        for u, v in portals.values():
            self.adjlist[u].append(v)
            self.adjlist[v].append(u)

    def shortest_distance(self) -> int:
        distances = {self.src_pos: 0}
        queue = collections.deque([self.src_pos])
        while queue:
            pos = queue.popleft()
            for adj_pos in self.adjlist[pos]:
                if adj_pos in distances:
                    continue
                distances[adj_pos] = distances[pos] + 1
                queue.append(adj_pos)
        return distances[self.dest_pos]


def read_input_file(filename: str) -> Graph:
    """
    Extracts a top view underground vault grid.
    """
    with open(filename) as fobj:
        grid = {
            Vec(col, row): char
            for row, line in enumerate(fobj)
            for col, char in enumerate(line.strip('\n'))
        }
    return Graph(grid)


if __name__ == '__main__':
    main()
