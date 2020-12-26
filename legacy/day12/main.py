"""
Day 12: The N-Body Problem
"""
import itertools
import math
import os
import re
from typing import Iterable, Iterator, List, NamedTuple, Sequence, Tuple, TypeVar

T = TypeVar('T')

point3d_re = re.compile(
    r"<\s*"
    r"x\s*=\s*(?P<x>-?[0-9]+)"
    r"\s*,\s*"
    r"y\s*=\s*(?P<y>-?[0-9]+)"
    r"\s*,\s*"
    r"z\s*=\s*(?P<z>-?[0-9]+)"
    r"\s*>",
)


####################
# Data definitions #
####################

class State(NamedTuple):
    """
    Information about the state of a single body on a particular axis.
    """
    pos: int
    vel: int = 0

    def go_next(self, acl: int) -> 'State':
        next_vel = self.vel + acl
        next_pos = self.pos + next_vel
        return State(next_pos, next_vel)

    def grav_single(self, other: 'State') -> int:
        if other.pos > self.pos:
            return 1
        if other.pos < self.pos:
            return -1
        return 0

    def gravitation(self, others: Iterable['State']) -> int:
        return sum(self.grav_single(other) for other in others)

    def next_from_gravitation(self, others: Iterable['State']) -> 'State':
        acl = self.gravitation(others)
        return self.go_next(acl)


class PeriodAndOffset(NamedTuple):
    period: int
    offset: int


##################
# Main functions #
##################

def one_and_rest(values: Sequence[T]) -> Iterator[Tuple[T, Iterator[T]]]:
    """
    Separate a given sequence into an iterator of each element
    and a sub-iterator of the rest of the elements.
    ABCDE -> (A, BCDE), (B, ACDE), (C, ABDE), (D, ABCE), (E, ABCD).
    """

    def _rest(skipping_index: int) -> Iterator[T]:
        yield from (
            value
            for index, value in enumerate(values)
            if index != skipping_index
        )

    yield from (
        (value, _rest(index))
        for index, value in enumerate(values)
    )


def read_states(filename: str) -> Tuple[List[State], List[State], List[State]]:
    x_states = []
    y_states = []
    z_states = []
    with open(filename) as fobj:
        for line in fobj:
            matchobj = point3d_re.fullmatch(line.strip())
            data = matchobj.groupdict()
            data = {key: int(value) for key, value in data.items()}
            x_states.append(State(pos=data['x']))
            y_states.append(State(pos=data['y']))
            z_states.append(State(pos=data['z']))
    return x_states, y_states, z_states


def next_state_single_axis(body_states: List[State]) -> List[State]:
    return [
        main.next_from_gravitation(others)
        for main, others in one_and_rest(body_states)
    ]


def energy(x_state: State, y_state: State, z_state: State) -> int:
    pot = abs(x_state.pos) + abs(y_state.pos) + abs(z_state.pos)
    kin = abs(x_state.vel) + abs(y_state.vel) + abs(z_state.vel)
    return pot * kin


def p1_time_step(
        x_states: List[State],
        y_states: List[State],
        z_states: List[State],
        steps: int,
):
    for _ in range(steps):
        x_states = next_state_single_axis(x_states)
        y_states = next_state_single_axis(y_states)
        z_states = next_state_single_axis(z_states)

    total_energy = sum(
        energy(*xyz_state)
        for xyz_state in zip(x_states, y_states, z_states)
    )
    print(f"Part one: {total_energy=}")


#######################
# Part two additional #
#######################

def step_and_cycle(states: List[State]) -> PeriodAndOffset:
    seen = {tuple(states): 0}
    for i in itertools.count(start=1):
        states = next_state_single_axis(states)
        tuple_states = tuple(states)
        if tuple_states in seen:
            return PeriodAndOffset(i - seen[tuple_states], seen[tuple_states])
        seen[tuple_states] = i


def p2_find_loop(x_states: List[State], y_states: List[State], z_states: List[State]):
    x_period, x_offset = step_and_cycle(x_states)
    y_period, y_offset = step_and_cycle(y_states)
    z_period, z_offset = step_and_cycle(z_states)
    assert x_offset == 0 and y_offset == 0 and z_offset == 0

    period = x_period * y_period // math.gcd(x_period, y_period)
    period = period * z_period // math.gcd(period, z_period)
    print(f"Part two: {period=}")


if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    positions_filename = os.path.join(this_dir, "positions.txt")
    x_states, y_states, z_states = read_states(positions_filename)

    # x_states = [State(-1), State(2), State(4), State(3)]
    # y_states = [State(0), State(-10), State(8), State(5)]
    # z_states = [State(2), State(-7), State(8), State(-1)]

    p1_time_step(x_states, y_states, z_states, steps=1000)
    p2_find_loop(x_states, y_states, z_states)
