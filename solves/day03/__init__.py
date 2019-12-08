"""
Day 3: Crossed Wires
"""
import os
from typing import Dict, Iterable, Iterator, List, NamedTuple, Tuple

this_dir = os.path.dirname(os.path.abspath(__file__))
wires_file = os.path.join(this_dir, "wires.txt")


class Point2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Point2D(self.x + other.x, self.y + other.y)

    def dist_from_origin(self):
        return abs(self.x) + abs(self.y)


Instruction = Tuple[Point2D, int]

symbol_to_direction = {
    'U': Point2D(0, 1),
    'D': Point2D(0, -1),
    'R': Point2D(1, 0),
    'L': Point2D(-1, 0),
}


def read_wires(file) -> Tuple[List[Instruction], List[Instruction]]:
    with open(file) as fobj:
        fst = parse_instructions(fobj.readline())
        snd = parse_instructions(fobj.readline())
        return fst, snd


def parse_instructions(line: str) -> List[Instruction]:
    instructions = []
    for instr in line.strip().split(","):
        direction = symbol_to_direction[instr[0]]
        steps = int(instr[1:])
        instructions.append((direction, steps))
    return instructions


def generate_occupancies(instructions: Iterable[Instruction]) -> Iterator[Point2D]:
    location = Point2D(0, 0)
    for direction, steps in instructions:
        for _ in range(steps):
            location = location + direction
            yield location


def occupancy_steps(instructions: Iterable[Instruction]) -> Dict[Point2D, int]:
    steps_data = {}
    for step, location in enumerate(generate_occupancies(instructions), start=1):
        if location in steps_data:
            continue
        steps_data[location] = step
    return steps_data


def solve_part_one():
    fst_instructions, snd_instructions = read_wires(wires_file)
    fst_occupancies = set(generate_occupancies(fst_instructions))
    snd_occupancies = set(generate_occupancies(snd_instructions))
    intersections = fst_occupancies & snd_occupancies
    result = min(inter.dist_from_origin() for inter in intersections)
    print(result)


def solve_part_two():
    fst_instructions, snd_instructions = read_wires(wires_file)
    fst_steps_data = occupancy_steps(fst_instructions)
    snd_steps_data = occupancy_steps(snd_instructions)
    intersections = fst_steps_data.keys() & snd_steps_data.keys()
    result = min(fst_steps_data[inter] + snd_steps_data[inter]
                 for inter in intersections)
    print(result)


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
