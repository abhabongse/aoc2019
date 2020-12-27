from __future__ import annotations

import os
from dataclasses import dataclass
from typing import NamedTuple

from mysolution.machine import Interface, Machine, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    machine = Machine(instructions, PainterInterface(starting_panel=0))
    machine.run_until_terminate()
    p1_answer = len(machine.interface.canvas)
    print(p1_answer)

    # Part 2
    machine = Machine(instructions, PainterInterface(starting_panel=1))
    machine.run_until_terminate()
    machine.interface.paint_image()


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

    def rotate_left(self) -> Vec:
        return Vec(x=-self.y, y=self.x)

    def rotate_right(self) -> Vec:
        return Vec(x=self.y, y=-self.x)


@dataclass(init=False)
class PainterInterface(Interface):
    robot_pos: Vec
    robot_heading: Vec
    canvas: dict[Vec, int]
    out_buffer: list[int]

    def __init__(self, starting_panel: int = 0):
        self.robot_pos = Vec(0, 0)
        self.robot_heading = Vec(0, 1)
        self.canvas = {self.robot_pos: starting_panel}
        self.out_buffer = []

    def input(self) -> int:
        return self.canvas.get(self.robot_pos, 0)

    def output(self, value: int):
        self.out_buffer.append(value)
        if len(self.out_buffer) == 2:
            self.paint_panel(self.out_buffer[0])
            self.turn_and_move(self.out_buffer[1])
            self.out_buffer = []

    def paint_panel(self, value: int):
        self.canvas[self.robot_pos] = value

    def turn_and_move(self, turn: int):
        if turn == 0:
            self.robot_heading = self.robot_heading.rotate_left()
        elif turn == 1:
            self.robot_heading = self.robot_heading.rotate_right()
        else:
            raise ValueError(f"unknown turning instruction: {turn!r}")
        self.robot_pos += self.robot_heading

    def paint_canvas(self):
        black_pixels = frozenset(pixel for pixel, blacked in self.canvas.items() if blacked)
        x_bound = range(min(p.x for p in black_pixels), max(p.x for p in black_pixels) + 1)
        y_bound = range(min(p.y for p in black_pixels), max(p.y for p in black_pixels) + 1)

        for y in reversed(y_bound):
            buffer = ''.join('#' if Vec(x, y) in black_pixels else ' ' for x in x_bound)
            print(buffer)


if __name__ == '__main__':
    main()
