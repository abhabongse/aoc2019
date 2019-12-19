"""
Day 3: Crossed Wires
"""
import os
from typing import Dict, Iterable, Iterator, List, NamedTuple, Tuple


####################
# Data definitions #
####################

class Vector2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)

    def norm1(self) -> int:
        return abs(self.x) + abs(self.y)


class Walk(NamedTuple):
    direction: Vector2D
    steps: int


SYMBOL_TO_DIRECTION = {
    'U': Vector2D(0, 1),
    'D': Vector2D(0, -1),
    'R': Vector2D(1, 0),
    'L': Vector2D(-1, 0),
}


##################
# Main functions #
##################

def read_wires(filename: str) -> Tuple[List[Walk], List[Walk]]:
    with open(filename) as fobj:
        fst_instrs = parse_walk_instrs(fobj.readline())
        snd_instrs = parse_walk_instrs(fobj.readline())
        return fst_instrs, snd_instrs


def parse_walk_instrs(line: str) -> List[Walk]:
    walks = []
    for walk in line.strip().split(","):
        direction = SYMBOL_TO_DIRECTION[walk[0]]
        steps = int(walk[1:])
        walk = Walk(direction, steps)
        walks.append(walk)
    return walks


def walked_cells(instructions: Iterable[Walk]) -> Iterator[Vector2D]:
    """
    Converts from a sequence of walking instructions from the point of origin
    into a sequence of traversed positions.
    """
    location = Vector2D(0, 0)
    for direction, steps in instructions:
        for _ in range(steps):
            location += direction
            yield location


def first_step_count_to_cells(instructions: Iterable[Walk]) -> Dict[Vector2D, int]:
    """
    From the given walking instructions, computes the mapping
    from each traversed cell to the first step count to such position.
    """
    step_count_data = {}
    for count, location in enumerate(walked_cells(instructions), start=1):
        if location in step_count_data:
            continue  # already exists
        step_count_data[location] = count
    return step_count_data


def p1_closest_intersection(fst_instrs, snd_instrs):
    fst_walked_cells = set(walked_cells(fst_instrs))
    snd_walked_cells = set(walked_cells(snd_instrs))

    intersections = fst_walked_cells & snd_walked_cells
    closest_norm1_dist = min(inter.norm1() for inter in intersections)
    print(f"Part one: {closest_norm1_dist=}")


def p2_fewest_step_intersections(fst_instrs, snd_instrs):
    fst_step_count_data = first_step_count_to_cells(fst_instrs)
    snd_steps_count_data = first_step_count_to_cells(snd_instrs)

    intersections = fst_step_count_data.keys() & snd_steps_count_data.keys()
    fewest_step_norm1_dist = min(
        fst_step_count_data[inter] + snd_steps_count_data[inter]
        for inter in intersections
    )
    print(f"Part two: {fewest_step_norm1_dist=}")


if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    wires_filename = os.path.join(this_dir, "wires.txt")
    fst_instrs, snd_instrs = read_wires(wires_filename)

    p1_closest_intersection(fst_instrs, snd_instrs)
    p2_fewest_step_intersections(fst_instrs, snd_instrs)
