from __future__ import annotations

import os
from collections.abc import Iterator, Sequence
from dataclasses import InitVar, dataclass, field
from typing import Union

from mysolution.geometry import Vec
from mysolution.machine import KeyboardPort, Machine, QueuePort, ScreenPort, load_instructions

MoveFunc = Sequence[Union[int, str]]

ORTHOGONAL_STEPS = [Vec(1, 0), Vec(0, 1), Vec(-1, 0), Vec(0, -1)]
SCAFFOLD_CHARS = '#^v<>'


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    machine = Machine(instructions, KeyboardPort(), ScreenPort(silent=True))
    machine.run_until_terminate()
    print(''.join(chr(c) for c in machine.output_tape))

    image = Image(machine.output_tape)
    p1_answer = sum(x * y for x, y in image.intersections())
    print(p1_answer)

    # Part 2 (solved for particular input by hand)
    main_routine = 'ABBCCAABBC'
    func_a = ['L', 12, 'R', 4, 'R', 4]
    func_b = ['R', 12, 'R', 4, 'L', 12]
    func_c = ['R', 12, 'R', 4, 'L', 6, 'L', 8, 'L', 8]
    movements = prepare_movements(main_routine, func_a, func_b, func_c)

    input_port = QueuePort([ord(c) for c in movements])
    machine = Machine(instructions, input_port, ScreenPort(silent=True))
    machine.memory[0] = 2
    machine.run_until_terminate()

    p2_answer = machine.output_tape[-1]
    print(p2_answer)


@dataclass
class Image:
    image_buffer: InitVar[Sequence[int]]
    area: dict[Vec, str] = field(default_factory=dict, init=False)

    def __post_init__(self, image_buffer: Sequence[int]):
        pos = Vec(0, 0)
        for char in image_buffer:
            char = chr(char)
            if char == '\n':
                pos = Vec(pos.x + 1, 0)
            else:
                self.area[pos] = char
                pos += Vec(0, 1)

    def intersections(self) -> Iterator[Vec]:
        """
        Produces a list of positions of all intersections.
        """
        for pos, char in self.area.items():
            if char not in SCAFFOLD_CHARS:
                continue
            if all(self.area.get(pos + step, '.') in SCAFFOLD_CHARS for step in ORTHOGONAL_STEPS):
                yield pos


def prepare_movements(main_routine: str, func_a: MoveFunc, func_b: MoveFunc, func_c: MoveFunc) -> str:
    """
    Prepare input string for the ascii program.
    """
    main_routine = ','.join(main_routine)
    func_a = ','.join(str(x) for x in func_a)
    func_b = ','.join(str(x) for x in func_b)
    func_c = ','.join(str(x) for x in func_c)
    return f'{main_routine}\n{func_a}\n{func_b}\n{func_c}\nn\n'


if __name__ == '__main__':
    main()
