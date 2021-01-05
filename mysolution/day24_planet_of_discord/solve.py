from __future__ import annotations

import collections
import itertools
import os
from collections.abc import Iterator, Set
from typing import NamedTuple

from mysolution.geometry import Vec

WIDTH = 5
HEIGHT = 5
ORTHOGONAL_STEPS = [Vec(1, 0), Vec(0, 1), Vec(-1, 0), Vec(0, -1)]


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    initial_bugs = read_input_files(input_file)

    # Part 1
    bugs = initial_bugs
    observed_ratings = {biodiversity_rating(bugs)}
    while True:
        bugs = next_normal_grid(bugs)
        rating = biodiversity_rating(bugs)
        if rating in observed_ratings:
            break
        observed_ratings.add(rating)
    p1_answer = rating
    print(p1_answer)

    # Part 2
    bugs = frozenset(LeveledPosition(pos, level=0) for pos in initial_bugs)
    for _ in range(200):
        bugs = next_recursive_grid(bugs)
    # pprint(sorted(bugs, key=lambda p: (p.level, p)))
    p2_answer = len(bugs)
    print(p2_answer)


class LeveledPosition(NamedTuple):
    """
    Position in the infinitely recursive grid.
    """
    coords: Vec
    level: int


def next_normal_grid(bugs: Set[Vec]) -> frozenset[Vec]:
    """
    Simulates the next grid state of the ERIS planet.
    """
    nbr_counts = collections.Counter(
        pos + step
        for pos in bugs
        for step in ORTHOGONAL_STEPS
    )
    next_bugs = frozenset(
        pos for r, c in itertools.product(range(HEIGHT), range(WIDTH))
        if (pos := Vec(r, c)) not in bugs and nbr_counts[pos] == 2 or nbr_counts[pos] == 1
    )
    return next_bugs


def biodiversity_rating(bugs: Set[Vec]) -> int:
    """
    Computes the bio-diversity rating for a collection of bug positions.
    """
    rating = sum(
        1 << (r * WIDTH + c)
        for r, c in itertools.product(range(HEIGHT), range(WIDTH))
        if Vec(c, r) in bugs
    )
    return rating


def next_recursive_grid(bugs: Set[LeveledPosition]) -> frozenset[LeveledPosition]:
    """
    Simulates the next recursive grid state of the ERIS planet.
    """
    nbr_counts = collections.Counter(
        adj_pos
        for pos in bugs
        for adj_pos in generate_adjacent_positions(pos)
    )
    next_bugs = frozenset(
        pos
        for pos, count in nbr_counts.items()
        if pos not in bugs and count == 2 or count == 1
    )
    return next_bugs


def generate_adjacent_positions(pos: LeveledPosition) -> Iterator[LeveledPosition]:
    """
    Produces a sequence of adjacent positions in all levels.
    """
    for step in ORTHOGONAL_STEPS:
        adj_coords = pos.coords + step
        if adj_coords == Vec(2, 2):
            x_candidates = _translate_to_candidates(WIDTH, step.x)
            y_candidates = _translate_to_candidates(HEIGHT, step.y)
            for x, y in itertools.product(x_candidates, y_candidates):
                yield LeveledPosition(Vec(x, y), pos.level + 1)
        elif adj_coords.x in range(WIDTH) and adj_coords.y in range(HEIGHT):
            yield LeveledPosition(adj_coords, pos.level)
        else:
            yield LeveledPosition(step + Vec(2, 2), pos.level - 1)


def _translate_to_candidates(size: int, step: int) -> Iterator[int]:
    if step == 0:
        yield from range(size)
    elif step == 1:
        yield 0
    elif step == -1:
        yield size - 1
    else:
        raise ValueError(step)


def read_input_files(input_file: str) -> frozenset[Vec]:
    """
    Extracts a set of positions on the ERIS planet manifested with bugs.
    """
    with open(input_file) as fobj:
        bugs = frozenset(
            Vec(col, row)
            for row, line in enumerate(fobj)
            for col, char in enumerate(line.strip())
            if char == '#'
        )
    return bugs


if __name__ == '__main__':
    main()
