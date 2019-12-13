"""
Day 3: Crossed Wires
"""
import os
from typing import Dict, Iterable, Iterator, List, NamedTuple, Tuple

this_dir = os.path.dirname(os.path.abspath(__file__))
wires_filename = os.path.join(this_dir, "wires.txt")


####################
# Data definitions #
####################

class Vector2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def norm1(self):
        return abs(self.x) + abs(self.y)


Instruction = Tuple[Vector2D, int]

SYMBOL_TO_DIRECTION = {
    'U': Vector2D(0, 1),
    'D': Vector2D(0, -1),
    'R': Vector2D(1, 0),
    'L': Vector2D(-1, 0),
}


##################
# Main functions #
##################

def read_wires(filename: str) -> Tuple[List[Instruction], List[Instruction]]:
    with open(filename) as fobj:
        fst = parse_instructions(fobj.readline())
        snd = parse_instructions(fobj.readline())
        return fst, snd


def parse_instructions(line: str) -> List[Instruction]:
    instructions = []
    for instr in line.strip().split(","):
        direction = SYMBOL_TO_DIRECTION[instr[0]]
        steps = int(instr[1:])
        instr = (direction, steps)
        instructions.append(instr)
    return instructions


def traversed_cells(instructions: Iterable[Instruction]) -> Iterator[Vector2D]:
    """
    Convert from a sequence of walking instructions from the point of origin
    into a sequence of traversed positions.
    """
    location = Vector2D(0, 0)
    for direction, steps in instructions:
        for _ in range(steps):
            location += direction
            yield location


def first_step_count_to_cells(
        instructions: Iterable[Instruction],
) -> Dict[Vector2D, int]:
    """
    From the given walking instructions, computes the mapping
    from each traversed cell to the first step count to such position.
    """
    step_count_data = {}
    for count, location in enumerate(traversed_cells(instructions), start=1):
        if location in step_count_data:
            continue  # already exists
        step_count_data[location] = count
    return step_count_data


def solve_part_one():
    fst_instructions, snd_instructions = read_wires(wires_filename)

    fst_traversed_cells = set(traversed_cells(fst_instructions))
    snd_traversed_cells = set(traversed_cells(snd_instructions))

    intersections = fst_traversed_cells & snd_traversed_cells
    result = min(inter.norm1() for inter in intersections)
    print(f"Part one: {result=}")


def solve_part_two():
    fst_instructions, snd_instructions = read_wires(wires_filename)

    fst_step_count_data = first_step_count_to_cells(fst_instructions)
    snd_steps_count_data = first_step_count_to_cells(snd_instructions)

    intersections = fst_step_count_data.keys() & snd_steps_count_data.keys()
    result = min(
        fst_step_count_data[inter] + snd_steps_count_data[inter]
        for inter in intersections
    )
    print(f"Part two: {result=}")


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
