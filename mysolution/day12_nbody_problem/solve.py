from __future__ import annotations

import functools
import itertools
import math
import os
import re
from collections.abc import Iterable, Iterator, Sequence
from typing import NamedTuple, TypeVar

T = TypeVar('T')
StateVector = Sequence['StateScalar']
Period = int
Offset = int

COORDS_RE = re.compile(r'<x=(-?\d+), y=(-?\d+), z=(-?\d+)>')


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    initial_vectors = read_input_file(input_file)

    # Part 1
    updated_vectors = simulate(initial_vectors, repeat=1000)
    p1_answer = sum(energy(nd_state) for nd_state in updated_vectors)
    print(p1_answer)

    # Part 2
    p2_answer = find_simulation_period(initial_vectors)
    print(p2_answer)


class StateScalar(NamedTuple):
    """
    Represents a planet physical state (position and velocity) in one dimension.
    """
    pos: int
    vel: int = 0

    def next_state(self, others: Iterable[StateScalar]) -> StateScalar:
        acl = sum(self.acl_pulled_by(p) for p in others)
        next_vel = self.vel + acl
        next_pos = self.pos + next_vel
        return StateScalar(next_pos, next_vel)

    def acl_pulled_by(self, other: StateScalar) -> int:
        if self.pos < other.pos:
            return 1
        elif self.pos > other.pos:
            return -1
        else:
            return 0


def simulate(initial_vectors: Sequence[StateVector], repeat: int) -> list[StateVector]:
    """
    Simulates position and velocity of celestial bodies repeatedly
    based on the given initial state.
    Data for each axis is simulated independently.
    """
    transposed_samples = []
    for sampled_scalars in zip(*initial_vectors):
        updated_sampled_scalars = functools.reduce(
            lambda ss, _: simulate_next_linear(ss),
            range(repeat), sampled_scalars,
        )
        transposed_samples.append(updated_sampled_scalars)
    updated_vectors = list(zip(*transposed_samples))
    return updated_vectors


def find_simulation_period(initial_vectors: Sequence[StateVector]) -> int:
    """
    Computes the length of period (i.e. cycle)
    when the simulation repeats itself  on every axis.
    """
    multidimensional_periods = []
    for sampled_scalars in zip(*initial_vectors):
        period, offset = simulate_linear_until_repeat(sampled_scalars)
        assert offset == 0
        multidimensional_periods.append(period)
    return math.lcm(*multidimensional_periods)


def simulate_linear_until_repeat(sampled_scalars: Sequence[StateScalar]) -> tuple[Period, Offset]:
    """
    Computes the offset and length of the period
    when the simulation repeats itself on a single axis.
    """
    sampled_scalars = tuple(sampled_scalars)
    recorded_offsets = {sampled_scalars: 0}
    for time in itertools.count(start=1):
        sampled_scalars = tuple(simulate_next_linear(sampled_scalars))
        if sampled_scalars in recorded_offsets:
            offset = recorded_offsets[sampled_scalars]
            period = time - offset
            return period, offset
        recorded_offsets[sampled_scalars] = time


def simulate_next_linear(sampled_scalars: Sequence[StateScalar]) -> Sequence[StateScalar]:
    """
    Simulates the next state of celestial bodies for a single time-step on a single axis.
    """
    updated_sampled_scalars = [
        primary.next_state(others)
        for primary, others in one_and_rest(sampled_scalars)
    ]
    return updated_sampled_scalars


def energy(vector: StateVector) -> int:
    """
    Computes the energy of one celestial body.
    """
    pot_energy = sum(abs(scalar.pos) for scalar in vector)
    kin_energy = sum(abs(scalar.vel) for scalar in vector)
    return pot_energy * kin_energy


def one_and_rest(values: Sequence[T]) -> Iterator[tuple[T, Iterator[T]]]:
    """
    Separates a given sequence into an iterator of each element
    plus a sub-iterator for the rest of the elements.
    Visualization: ABCDE -> (A, BCDE), (B, ACDE), (C, ABDE), (D, ABCE), (E, ABCD)
    """
    for primary, with_others in itertools.groupby(itertools.permutations(values, r=2), key=lambda p: p[0]):
        yield primary, (other for _, other in with_others)


def read_input_file(filename: str) -> list[StateVector]:
    """
    Extracts a list of initial states of Jupiter's moons.
    """
    with open(filename) as fobj:
        initial_vectors = [parse_initial_vector(line.strip()) for line in fobj]
    return initial_vectors


def parse_initial_vector(raw: str) -> StateVector:
    """
    Parses the initial state of one celestial body.
    """
    return [StateScalar(pos=int(token)) for token in COORDS_RE.fullmatch(raw).groups()]


if __name__ == '__main__':
    main()
