from __future__ import annotations

import os
import threading
from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from typing import NamedTuple

from mysolution.machine import Machine, QueuePort, ResourceUnavailable, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    brain_instructions = load_instructions(input_file)

    # Part 1
    painter = Painter(brain_instructions, starting_panel=0)
    painter.run_until_terminate()
    p1_answer = len(painter.canvas)
    print(p1_answer)

    # Part 2
    painter = Painter(brain_instructions, starting_panel=1)
    painter.run_until_terminate()
    painter.print_canvas()


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


@dataclass
class Painter:
    brain_instrs: InitVar[Sequence[int]]
    starting_panel: InitVar[int]

    camera: QueuePort = field(init=False)
    motor: QueuePort = field(init=False)
    brain: Machine = field(init=False)
    sigterm_flag: bool = field(default=False, init=False)

    robot_pos: Vec = Vec(0, 0)
    robot_heading: Vec = Vec(0, 1)
    canvas: dict[Vec, int] = field(init=False)

    def __post_init__(self, brain_instrs: Sequence[int], starting_panel: int):
        self.camera = QueuePort()
        self.motor = QueuePort()
        self.brain = Machine(brain_instrs, self.camera, self.motor)
        self.canvas = {self.robot_pos: starting_panel}

    def sigterm_received(self) -> bool:
        return self.sigterm_flag

    def run_until_terminate(self):
        thread = threading.Thread(target=self._run_subroutine)
        thread.start()
        self.brain.run_until_terminate()
        self.sigterm_flag = True
        thread.join()

    def _run_subroutine(self):
        while True:
            try:
                self.execute_next()
            except ResourceUnavailable:
                break

    def execute_next(self):
        self.camera.put(self.observe_panel(), self.sigterm_received)
        self.paint_panel(self.motor.get(self.sigterm_received))
        self.turn_and_move(self.motor.get(self.sigterm_received))

    def observe_panel(self) -> int:
        return self.canvas.get(self.robot_pos, 0)

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

    def print_canvas(self):
        black_pixels = frozenset(pixel for pixel, blacked in self.canvas.items() if blacked)
        x_bound = range(min(p.x for p in black_pixels), max(p.x for p in black_pixels) + 1)
        y_bound = range(min(p.y for p in black_pixels), max(p.y for p in black_pixels) + 1)

        for y in reversed(y_bound):
            buffer = ''.join('#' if Vec(x, y) in black_pixels else ' ' for x in x_bound)
            print(buffer)


if __name__ == '__main__':
    main()
