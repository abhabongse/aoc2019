from __future__ import annotations

import os
from collections.abc import Iterator, Sequence

from mysolution.geometry import Vec

Move = tuple[Vec, int]

DIRECTIONAL_STEPS = {
    'U': Vec(0, 1),
    'D': Vec(0, -1),
    'R': Vec(1, 0),
    'L': Vec(-1, 0),
}


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    fst_moves, snd_moves = read_input_file(input_file)

    # Part 1
    fst_positions = set(walked_positions(fst_moves))
    snd_positions = set(walked_positions(snd_moves))
    crossed_positions = fst_positions & snd_positions
    p1_answer = min(pos.norm1() for pos in crossed_positions)
    print(p1_answer)

    # Part 2
    fst_positions_with_counts = counts_to_walked_positions(fst_moves)
    snd_positions_with_counts = counts_to_walked_positions(snd_moves)
    crossed_positions = fst_positions_with_counts.keys() & snd_positions_with_counts.keys()
    p2_answer = min(
        fst_positions_with_counts[pos] + snd_positions_with_counts[pos]
        for pos in crossed_positions
    )
    print(p2_answer)


def walked_positions(moves: Sequence[Move]) -> Iterator[Vec]:
    """
    Produces a sequence of walked positions starting from a sequence of moves
    starting (but not including) the point of origin (0, 0).
    """
    current = Vec(0, 0)
    for direction, steps in moves:
        for _ in range(steps):
            current += direction
            yield current


def counts_to_walked_positions(moves: Sequence[Move]) -> dict[Vec, int]:
    """
    Computes the first step count towards each walked positions
    from a sequence of moves from the origin.
    """
    step_counts = {}
    for count, position in enumerate(walked_positions(moves), start=1):
        step_counts.setdefault(position, count)
    return step_counts


def read_input_file(filename: str) -> tuple[list[Move], list[Move]]:
    """
    Extracts two lists of wire moves.
    """
    with open(filename) as fobj:
        fst_moves = parse_wire_moves(next(fobj).strip())
        snd_moves = parse_wire_moves(next(fobj).strip())
    return fst_moves, snd_moves


def parse_wire_moves(raw: str) -> list[Move]:
    """
    Parses a sequence of moves for a single wire.
    """
    return [
        (DIRECTIONAL_STEPS[token[0]], int(token[1:]))
        for token in raw.split(',')
    ]


if __name__ == '__main__':
    main()
