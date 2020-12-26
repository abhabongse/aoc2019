from __future__ import annotations

import functools
import itertools
import math
import os
import re
from collections.abc import Iterable, Iterator, Sequence
from typing import Annotated, NamedTuple, TypeVar

T = TypeVar('T')

Position = list[int]
VectoredState = Sequence['ScalarState']
COORDS_RE = re.compile(r'<x=(-?\d+), y=(-?\d+), z=(-?\d+)>')


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    positions = read_input_file(input_file)

    # Part 1
    vectors = simulate(positions, repeat=1000)
    p1_answer = sum(energy(v) for v in vectors)
    print(p1_answer)

    # Part 2
    p2_answer = period_simulation_repeated(positions)
    print(p2_answer)


class ScalarState(NamedTuple):
    """
    One-dimensional planet state (position and velocity on a single axis).
    """
    pos: int
    vel: int = 0

    def next_state(self, others: Iterable[ScalarState]) -> ScalarState:
        acl = sum(self.acl_pulled_by(p) for p in others)
        next_vel = self.vel + acl
        next_pos = self.pos + next_vel
        return ScalarState(next_pos, next_vel)

    def acl_pulled_by(self, other: ScalarState) -> int:
        if self.pos < other.pos:
            return 1
        elif self.pos > other.pos:
            return -1
        else:
            return 0


def simulate(positions: Sequence[Position], repeat: int) -> list[VectoredState]:
    multidimensional_scalars = []
    for scalars in zip(*positions):
        scalars = [ScalarState(pos=s) for s in scalars]
        scalars = functools.reduce(lambda s, _: simulate_next_linear(s), range(repeat), scalars)
        multidimensional_scalars.append(scalars)
    vectors = list(zip(*multidimensional_scalars))
    return vectors


def period_simulation_repeated(positions: Sequence[Position]) -> int:
    multidimensional_periods = []
    for scalars in zip(*positions):
        scalars = [ScalarState(pos=s) for s in scalars]
        period, offset = simulate_linear_until_repeat(scalars)
        assert offset == 0
        multidimensional_periods.append(period)
    return math.lcm(*multidimensional_periods)


def simulate_linear_until_repeat(
        scalars: Sequence[ScalarState],
) -> tuple[Annotated[int, 'period'], Annotated[int, 'offset']]:  # noqa: F821
    recorded_offsets = {tuple(scalars): 0}
    for time in itertools.count(start=1):
        scalars = simulate_next_linear(scalars)
        tuple_scalars = tuple(scalars)
        if tuple_scalars in recorded_offsets:
            offset = recorded_offsets[tuple_scalars]
            period = time - offset
            return period, offset
        recorded_offsets[tuple_scalars] = time


def simulate_next_linear(scalars: Sequence[ScalarState]) -> list[ScalarState]:
    next_states = [
        primary.next_state(others)
        for primary, others in one_and_rest(scalars)
    ]
    return next_states


def energy(vectored_state: VectoredState) -> int:
    pot_energy = sum(abs(singular.pos) for singular in vectored_state)
    kin_energy = sum(abs(singular.vel) for singular in vectored_state)
    return pot_energy * kin_energy


def one_and_rest(values: Sequence[T]) -> Iterator[tuple[T, Iterator[T]]]:
    """
    Separates a given sequence into an iterator of each element
    plus a sub-iterator for the rest of the elements.
    Visualization: ABCDE -> (A, BCDE), (B, ACDE), (C, ABDE), (D, ABCE), (E, ABCD)
    """
    for primary, with_others in itertools.groupby(itertools.permutations(values, r=2), key=lambda p: p[0]):
        yield primary, (other for _, other in with_others)


def read_input_file(filename: str) -> list[Position]:
    """
    Extracts a list of initial Jupiter's moon positions.
    """
    with open(filename) as fobj:
        positions = [parse_initial_state(line.strip()) for line in fobj]
    return positions


def parse_initial_state(raw: str) -> Position:
    return [int(token) for token in COORDS_RE.fullmatch(raw).groups()]


if __name__ == '__main__':
    main()
