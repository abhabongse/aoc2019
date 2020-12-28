from __future__ import annotations

import enum
import os
import time
from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from typing import ClassVar

from mysolution.machine import ProcessTerminated, QueuedPort, Machine, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    machine = Machine(instructions, ArcadeQueuedPort())
    machine.run_until_terminate()
    p1_answer = sum(tile == 2 for tile in machine.port.canvas.values())
    print(p1_answer)

    # Part 2
    machine = Machine(instructions, AutoArcadeInterface())
    # machine = Machine(instructions, ArcadeInterface())
    machine.memory[0] = 2  # insert coin
    machine.run_until_terminate()
    p2_answer = machine.port.score
    print(p2_answer)


class Tile(enum.IntEnum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4


@dataclass
class Arcade:
    chip_instrs: InitVar[Sequence[int]]
    paddle: int = field(init=False, default=None)
    ball: int = field(init=False, default=None)
    score: int = field(init=False, default=None)

    joystick: QueuedPort = field(default_factory=QueuedPort, init=False)
    display: QueuedPort = field(default_factory=QueuedPort, init=False)
    chip: Machine = field(init=False)

    tile_chars: ClassVar[str] = ' #$_o'

    def __post_init__(self, chip_instrs: Sequence[int]):
        self.chip = Machine(chip_instrs, self.joystick, self.display)

    def run_until_terminate(self):
        thread = threading.Thread(target=self._run_body)
        thread.start()
        self.chip.run_until_terminate()
        thread.join()

    def _run_body(self):
        while True:
            try:
                self.execute_next()
            except ProcessTerminated:
                break

    def execute_next(self):






@dataclass
class ArcadeQueuedPort(QueuedPort):
    canvas: dict[tuple[int, int], int] = field(init=False, default_factory=dict)
    out_buffer: list[int] = field(init=False, default_factory=list)
    paddle: int = field(init=False, default=None)
    ball: int = field(init=False, default=None)
    score: int = field(init=False, default=None)
    tile_chars: ClassVar[str] = ' #$_O'

    def input(self) -> int:
        self.print_board()
        value = input("Enter Q or P (move left/right): ").strip()
        if value.upper() == 'Q':
            return -1
        elif value.upper() == 'P':
            return 1
        else:
            return 0

    def output(self, value: int):
        self.out_buffer.append(value)
        if len(self.out_buffer) == 3:
            x, y, value = self.out_buffer
            self.draw_tile(x, y, value)
            self.out_buffer = []

    def draw_tile(self, x: int, y: int, value: int):
        if (x, y) == (-1, 0):
            self.score = value
        else:
            self.canvas[x, y] = value
            if value == Tile.PADDLE:
                self.paddle = x
            if value == Tile.BALL:
                self.ball = x

    def print_board(self):
        x_bound = range(min(p[0] for p in self.canvas.keys()), max(p[0] for p in self.canvas.keys()) + 1)
        y_bound = range(min(p[1] for p in self.canvas.keys()), max(p[1] for p in self.canvas.keys()) + 1)

        for y in y_bound:
            print_buffer = ''.join(self.tile_chars[self.canvas[x, y]] for x in x_bound)
            print(print_buffer)


@dataclass
class AutoArcadeInterface(ArcadeQueuedPort):
    display_delay: float = None

    def input(self) -> int:
        if self.display_delay:
            self.print_board()
            time.sleep(self.display_delay)
        if self.ball < self.paddle:
            return -1
        elif self.ball > self.paddle:
            return 1
        else:
            return 0


if __name__ == '__main__':
    main()
