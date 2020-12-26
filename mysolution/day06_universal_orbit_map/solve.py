from __future__ import annotations

import os
from collections.abc import Iterator
from graphlib import TopologicalSorter  # noqa: I201


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    orbits = read_input_file(input_file)

    # Part 1
    depths = node_depths(orbits)
    p1_answer = sum(depths.values())
    print(p1_answer)

    # Part 2
    you_ancestors = set(node_ancestors('YOU', orbits))
    san_ancestors = set(node_ancestors('SAN', orbits))
    p2_answer = len(you_ancestors) + len(san_ancestors) - 2 * len(you_ancestors & san_ancestors)
    print(p2_answer)


def node_depths(parents_map: dict[str, str]) -> dict[str, int]:
    """
    Computes tree depth for each node in the tree
    described by the give root and a mapping of each node to its parent.
    """
    sorter = TopologicalSorter({node: [parent] for node, parent in parents_map.items()})
    depths = {}
    for node in sorter.static_order():
        depths[node] = depths[parents_map[node]] + 1 if node in parents_map else 0
    return depths


def node_ancestors(node: str, parents_map: dict[str, str]) -> Iterator[str]:
    """
    Produces a sequence of ancestors from direct parent to root.
    """
    while node in parents_map:
        node = parents_map[node]
        yield node


def read_input_file(filename: str) -> dict[str, str]:
    """
    Extracts a list of orbit pairs.
    """
    with open(filename) as fobj:
        orbits = dict(parse_orbit_pair(line) for line in fobj)
    return orbits


def parse_orbit_pair(raw: str) -> tuple[str, str]:
    """
    Parses an orbit pair as a pair of (satellite, center).
    """
    center, satellite = raw.strip().split(')')
    return satellite, center


if __name__ == '__main__':
    main()
