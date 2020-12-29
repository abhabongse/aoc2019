from __future__ import annotations

import enum
import os
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

import more_itertools

from mysolution.machine import Machine, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    controller = ArcadeController()
    machine = Machine(instructions, controller, controller)
    machine.run_until_terminate()
    controller.display.print_board()
    p1_answer = sum(tile == Tile.BLOCK for tile in controller.display.board.values())
    print(p1_answer)

    # Part 2
    controller = AutoArcadeController(display_with_delay=0.02)
    machine = Machine(instructions, controller, controller)
    machine.memory[0] = 2  # insert coin
    machine.run_until_terminate()
    p2_answer = controller.display.score
    print(p2_answer)


class Tile(enum.IntEnum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4


@dataclass
class ArcadeDisplay:
    board: dict[tuple[int, int], int] = field(default_factory=dict, init=False)
    paddle: int = field(default=None, init=False)
    ball: int = field(default=None, init=False)
    score: int = field(default=None, init=False)
    tile_chars: ClassVar[str] = ' #$_O'

    def update_from_draw_buffer(self, buffer: Sequence[int]):
        for x, y, value in more_itertools.chunked(buffer, n=3, strict=True):
            if (x, y) == (-1, 0):
                self.score = value
            else:
                self.board[x, y] = value
                if value == Tile.PADDLE:
                    self.paddle = x
                if value == Tile.BALL:
                    self.ball = x

    def print_board(self):
        x_bound = range(min(p[0] for p in self.board.keys()), max(p[0] for p in self.board.keys()) + 1)
        y_bound = range(min(p[1] for p in self.board.keys()), max(p[1] for p in self.board.keys()) + 1)

        for y in y_bound:
            print_buffer = ''.join(self.tile_chars[self.board[x, y]] for x in x_bound)
            print(print_buffer)


@dataclass
class ArcadeController:
    draw_buffer: list[int] = field(default_factory=list, init=False)
    display: ArcadeDisplay = field(default_factory=ArcadeDisplay, init=False)
    move_map: ClassVar[dict[str, int]] = {'Q': -1, 'P': 1}

    def get(self, _sentinel: Callable[[], bool] = None) -> int:
        self.display.print_board()
        value = input("Enter [QP] to move left/right: ").strip().upper()
        return self.move_map.get(value, 0)

    def put(self, value: int, _sentinel: Callable[[], bool] = None):
        self.draw_buffer.append(value)
        if len(self.draw_buffer) == 3:
            self.display.update_from_draw_buffer(self.draw_buffer)
            self.draw_buffer = []


@dataclass
class AutoArcadeController(ArcadeController):
    display_with_delay: float = None

    def get(self, _sentinel: Callable[[], bool] = None) -> int:
        if self.display_with_delay:
            self.display.print_board()
            time.sleep(self.display_with_delay)
        if self.display.ball < self.display.paddle:
            return -1
        elif self.display.ball > self.display.paddle:
            return 1
        else:
            return 0


if __name__ == '__main__':
    main()
