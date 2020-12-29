from __future__ import annotations

import os
import sys
import threading
from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from typing import TextIO

from mysolution.geometry import Vec
from mysolution.machine import Machine, QueuePort, ResourceUnavailable, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    chip_instructions = load_instructions(input_file)

    # Part 1
    painter = PainterRobot(chip_instructions, starting_panel=0)
    painter.run_until_terminate()
    p1_answer = len(painter.canvas)
    print(p1_answer)

    # Part 2
    painter = PainterRobot(chip_instructions, starting_panel=1)
    painter.run_until_terminate()
    painter.print_canvas()


@dataclass
class PainterRobot:
    """
    A painter robot with the following components:
    - core chip as the brain (running intcode machine),
    - a camera sensor (connected to input port of the core chip), and
    - motor mechanics (connected to output port) for painting and moving.
    """
    chip_instructions: InitVar[Sequence[int]]
    starting_panel: InitVar[int]

    core_chip: Machine = field(init=False)
    camera_port: QueuePort = field(default_factory=QueuePort, init=False)
    motor_port: QueuePort = field(default_factory=QueuePort, init=False)
    sigterm_flag: bool = field(default=False, init=False)

    robot_pos: Vec = Vec(0, 0)
    robot_heading: Vec = Vec(0, 1)
    canvas: dict[Vec, int] = field(init=False)

    def __post_init__(self, chip_instructions: Sequence[int], starting_panel: int):
        self.core_chip = Machine(chip_instructions, self.camera_port, self.motor_port)
        self.canvas = {self.robot_pos: starting_panel}

    def sigterm_received(self) -> bool:
        return self.sigterm_flag

    def run_until_terminate(self):
        """
        Runs the painter robot itself in a separate thread
        then terminate it once the core chip terminates.
        """
        thread = threading.Thread(target=self._run_subroutine)
        thread.start()
        self.core_chip.run_until_terminate()
        self.sigterm_flag = True
        thread.join()

    def _run_subroutine(self):
        while True:
            try:
                self.execute_next()
            except ResourceUnavailable:
                break

    def execute_next(self):
        """
        Performs the following sequence of steps:
        - Send the color of the current panel to the chip via camera port
        - Paint the current panel using info received via motor port
        - Turn and move to the next panel using info received via motor port
        """
        self.camera_port.put(self.observe_panel(), sentinel=self.sigterm_received)
        self.paint_panel(self.motor_port.get(sentinel=self.sigterm_received))
        self.turn_and_move(self.motor_port.get(sentinel=self.sigterm_received))

    def observe_panel(self) -> int:
        """
        Obtains the color of the current panel.
        """
        return self.canvas.get(self.robot_pos, 0)

    def paint_panel(self, color: int):
        """
        Paints the current panel with the given color.
        """
        self.canvas[self.robot_pos] = color

    def turn_and_move(self, turn_direction: int):
        """
        Rotates itself left or right then move forward one step.
        """
        if turn_direction == 0:
            self.robot_heading = self.robot_heading.turn('left')
        elif turn_direction == 1:
            self.robot_heading = self.robot_heading.turn('right')
        else:
            raise ValueError(f"unknown turning instruction: {turn_direction!r}")
        self.robot_pos += self.robot_heading

    def print_canvas(self, stream: TextIO = sys.stdout):
        """
        Prints whatever is on the canvas to the given stream.
        """
        black_pixels = frozenset(pixel for pixel, blacked in self.canvas.items() if blacked)
        x_bound = range(min(p.x for p in black_pixels), max(p.x for p in black_pixels) + 1)
        y_bound = range(min(p.y for p in black_pixels), max(p.y for p in black_pixels) + 1)

        for y in reversed(y_bound):
            buffer = ''.join('#' if Vec(x, y) in black_pixels else ' ' for x in x_bound)
            print(buffer, file=stream)


if __name__ == '__main__':
    main()
