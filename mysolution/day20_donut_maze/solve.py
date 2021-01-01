from __future__ import annotations

import collections
import os
import string
from dataclasses import InitVar, dataclass, field
from typing import NamedTuple

from mysolution.geometry import Vec

ORTHOGONAL_STEPS = [Vec(1, 0), Vec(0, 1), Vec(-1, 0), Vec(0, -1)]


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    graph = read_input_file(input_file)

    # Part 1
    p1_answer = graph.normal_space_shortest_distance()
    print(p1_answer)

    # Part 2
    p2_answer = graph.recursive_space_shortest_distance()
    print(p2_answer)


class LeveledPosition(NamedTuple):
    """
    Position in the donut maze consisting of the coordinates and the descending level.
    """
    coords: Vec
    level: int


@dataclass
class DonutMaze:
    """
    Graph representation of the donut maze grid as an adjacency list.
    Each node has a list of targets, each of which is a pair of
    target positions and changes in descending levels.
    """
    grid: InitVar[dict[Vec, str]]
    src_pos: Vec = field(init=False)
    dest_pos: Vec = field(init=False)
    adjlist: collections.defaultdict[Vec, list[tuple[Vec, int]]] = field(init=False)

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
                self.adjlist[pos].append((pos + step, 0))

    def _gather_portal_edges(self, grid: dict[Vec, str]):
        x_boundaries = range(2, max(p.x for p in grid.keys()) - 2)
        y_boundaries = range(2, max(p.y for p in grid.keys()) - 2)
        outer_portals = {}
        inner_portals = {}

        for pos, char in grid.items():
            if char != '.':
                continue
            for step in ORTHOGONAL_STEPS:
                adj_pos = pos + step
                if grid.get(adj_pos, '#') not in string.ascii_uppercase:
                    continue
                fst_pos, snd_pos = sorted([adj_pos, adj_pos + step])
                word = grid[fst_pos] + grid[snd_pos]
                if adj_pos.x in x_boundaries and adj_pos.y in y_boundaries:
                    inner_portals[word] = pos
                else:
                    outer_portals[word] = pos

        self.src_pos = outer_portals.pop('AA')
        self.dest_pos = outer_portals.pop('ZZ')

        assert outer_portals.keys() == inner_portals.keys()
        for word in outer_portals.keys():
            outer_pos = outer_portals[word]
            inner_pos = inner_portals[word]
            self.adjlist[outer_pos].append((inner_pos, -1))
            self.adjlist[inner_pos].append((outer_pos, +1))

    def normal_space_shortest_distance(self) -> int:
        """
        Finds the shortest path in the donut maze,
        ignoring the recursive descent property of the maze.
        """
        distances = {self.src_pos: 0}
        queue = collections.deque([self.src_pos])
        while queue:
            pos = queue.popleft()
            for next_pos, _ in self.adjlist[pos]:
                if next_pos in distances:
                    continue
                distances[next_pos] = distances[pos] + 1
                queue.append(next_pos)
                if next_pos == self.dest_pos:
                    return distances[next_pos]

    def recursive_space_shortest_distance(self) -> int:
        """
        Finds the shortest path in the donut maze,
        assuming that an inner portal connects to an outer one in the lower level.
        """
        src_node = LeveledPosition(self.src_pos, 0)
        dest_node = LeveledPosition(self.dest_pos, 0)
        distances = {src_node: 0}
        queue = collections.deque([src_node])
        while queue:
            node = queue.popleft()
            for next_pos, level_diff in self.adjlist[node.coords]:
                next_node = LeveledPosition(next_pos, node.level + level_diff)
                if next_node.level < 0 or next_node in distances:
                    continue
                distances[next_node] = distances[node] + 1
                queue.append(next_node)
                if next_node == dest_node:
                    return distances[next_node]


def read_input_file(filename: str) -> DonutMaze:
    """
    Extracts a top view underground vault grid.
    """
    with open(filename) as fobj:
        grid = {
            Vec(col, row): char
            for row, line in enumerate(fobj)
            for col, char in enumerate(line.strip('\n'))
        }
    return DonutMaze(grid)


if __name__ == '__main__':
    main()
