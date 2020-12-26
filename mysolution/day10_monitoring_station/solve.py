from __future__ import annotations

import collections
import math
import os
from collections.abc import Iterator, Sequence
from typing import NamedTuple

import more_itertools


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    asteroids = read_input_file(input_file)

    # Part 1
    visible_asteroids = {base: count_visible_asteroids(asteroids, base) for base in asteroids}
    station = max(visible_asteroids.keys(), key=lambda base: visible_asteroids[base])
    p1_answer = visible_asteroids[station]
    print(p1_answer)

    # Part 2
    n = 200
    bet_asteroid = more_itertools.nth(generate_destroyed_asteroids(asteroids, station), n - 1)
    p2_answer = bet_asteroid.x * 100 + bet_asteroid.y
    print(p2_answer)


class Vec(NamedTuple):
    x: int
    y: int

    def __pos__(self) -> Vec:
        return self

    def __neg__(self) -> Vec:
        return Vec(-self.x, -self.y)

    def __add__(self, other: Vec) -> Vec:
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec) -> Vec:
        return self + (-other)

    def norm2(self) -> int:
        return self.x ** 2 + self.y ** 2

    def reduce(self) -> Vec:
        d = math.gcd(self.x, self.y)
        return Vec(self.x // d, self.y // d)

    def wangle(self) -> float:
        return math.pi - math.atan2(self.x, self.y)


def count_visible_asteroids(asteroids: Sequence[Vec], base: Vec) -> int:
    reduced_rays = {(a - base).reduce() for a in asteroids if a != base}
    return len(reduced_rays)


def generate_destroyed_asteroids(asteroids: Sequence[Vec], base: Vec) -> Iterator[Vec]:
    rays = (a - base for a in asteroids if a != base)
    grouped_rays = collections.defaultdict(list)
    for r in rays:
        grouped_rays[r.reduce()].append(r)
    grouped_rays = [
        sorted(grouped_rays[reduced_ray], key=lambda r_: r_.norm2())
        for reduced_ray in sorted(grouped_rays.keys(), key=lambda rr: rr.wangle())
    ]
    for ray in more_itertools.roundrobin(*grouped_rays):
        yield ray + base


def read_input_file(filename: str) -> list[Vec]:
    """
    Extracts a list of asteroid positions.
    """
    with open(filename) as fobj:
        asteroids = [
            Vec(col, row)
            for row, line in enumerate(fobj)
            for col, char in enumerate(line.strip())
            if char == '#'
        ]
    return asteroids


if __name__ == '__main__':
    main()
