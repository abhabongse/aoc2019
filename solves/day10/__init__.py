"""
Day 10: Monitoring Station
"""
import itertools
import math
import os
from collections import defaultdict
from typing import List, NamedTuple

this_dir = os.path.dirname(os.path.abspath(__file__))
asteroids_filename = os.path.join(this_dir, "asteroids.txt")

selector = 200


class Vector2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)

    def norm2(self) -> int:
        return self.x ** 2 + self.y ** 2

    def reduce(self) -> 'Vector2D':
        d = math.gcd(self.x, self.y)
        return Vector2D(self.x // d, self.y // d)

    def wangle(self) -> float:
        return math.pi - math.atan2(self.x, self.y)


def roundrobin(*iterables):
    """
    roundrobin('ABC', 'D', 'EF') --> A D E B F C
    Copied from https://docs.python.org/3.8/library/itertools.html
    Recipe credited to George Sakkis.
    """
    num_active = len(iterables)
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = itertools.cycle(itertools.islice(nexts, num_active))


def read_asteroids(filename: str) -> List[Vector2D]:
    with open(filename) as fobj:
        return [
            Vector2D(col, row)
            for row, line in enumerate(fobj)
            for col, char in enumerate(line.strip())
            if char == '#'
        ]


def find_best_station(asteroids: List[Vector2D]) -> Vector2D:
    visible_counts = {}
    for base in asteroids:
        vectors = (  # orbiters in relative vector form
            orbiter - base
            for orbiter in asteroids
            if orbiter != base
        )
        visible_counts[base] = len({vec.reduce() for vec in vectors})
    station = max(visible_counts.keys(), key=visible_counts.__getitem__)
    print(f"Maximum asteroids of {visible_counts[station]} at {station}")
    return station


def solve_part_two(asteroids: List[Vector2D], station: Vector2D):
    vectors = (
        orbiter - station
        for orbiter in asteroids
        if orbiter != station
    )
    reduced_to_full = defaultdict(list)
    for vec in vectors:
        reduced_to_full[vec.reduce()].append(vec)

    # List of list of vectors.
    # Vectors in each inner list groups by its reduced from and sorts by its length.
    # Lists of vectors in the outer list sorts by its angle
    # starting from the top going in clockwise order.
    list_of_list_of_vectors = [
        sorted(reduced_to_full[reduced_vec], key=lambda vec: vec.norm2())
        for reduced_vec in sorted(reduced_to_full, key=lambda vec: vec.wangle())
    ]
    vaporized_asteroids = [
        station + vec
        for vec in roundrobin(*list_of_list_of_vectors)
    ]
    selected_asteroid = vaporized_asteroids[selector - 1]
    print(f"{selector}th vaporized asteroid is {selected_asteroid}")


def main():
    asteroids = read_asteroids(asteroids_filename)
    station = find_best_station(asteroids)  # part one
    solve_part_two(asteroids, station)


if __name__ == '__main__':
    main()
