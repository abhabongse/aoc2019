from __future__ import annotations

import os
import sys
import threading
from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from typing import TextIO

from mysolution.geometry import Vec
from mysolution.machine import Machine, Predicate, QueuePort, ResourceUnavailable, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    painter = PainterRobot(RobotChip(instructions), starting_panel=0)
    painter.deploy_robot()
    p1_answer = len(painter.canvas)
    print(p1_answer)

    # Part 2
    painter = PainterRobot(RobotChip(instructions), starting_panel=1)
    painter.deploy_robot()
    painter.print_canvas()


@dataclass
class PainterRobot:
    """
    A painter robot with the following components:
    - core chip as the brain (running intcode machine),
    - a camera sensor (connected to input port of the core chip), and
    - motor mechanics (connected to output port) for painting and moving.
    """
    chip: RobotChip
    sigterm: threading.Event = field(default_factory=threading.Event, init=False)
    starting_panel: InitVar[int]
    robot_pos: Vec = Vec(0, 0)
    robot_heading: Vec = Vec(0, 1)
    canvas: dict[Vec, int] = field(default_factory=dict, init=False)

    def __post_init__(self, starting_panel: int):
        self.canvas[self.robot_pos] = starting_panel

    def deploy_robot(self):
        """
        Runs the painter robot itself in a separate thread
        then terminate it once the core chip terminates.
        """
        thread = threading.Thread(target=self.observe_paint_move_loop)
        thread.start()
        self.chip.program.run_until_terminate()
        self.sigterm.set()
        thread.join()

    def observe_paint_move_loop(self):
        while True:
            try:
                new_color, turn_direction = self.chip.call(self.observe_panel(), self.sigterm.is_set)
                self.paint_panel(new_color)
                self.turn_and_move(turn_direction)
            except ResourceUnavailable:
                break

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


@dataclass
class RobotChip:
    """
    The brain of the painter robot which determines what the robot should do
    by reading the color of the current tile through the camera input port
    and command the robot to paint the new color on such tile
    and then move to a new tile through the motor output port.
    """
    instructions: InitVar[Sequence[int]]
    program: Machine = field(init=False)
    input_port: QueuePort = field(default_factory=QueuePort, init=False)
    output_port: QueuePort = field(default_factory=QueuePort, init=False)
    thread: threading.Thread = field(init=False)

    def __post_init__(self, instructions: Sequence[int]):
        self.program = Machine(instructions, self.input_port, self.output_port)

    def call(self, color: int, sentinel: Predicate) -> tuple[int, int]:
        """
        Runs a single sensory perception and motor response loop.
        The chip receives the color of the current tile
        and responses with the new color to paint and where to move next.
        """
        self.input_port.write_int(color, sentinel=sentinel)
        new_color, turn_direction = self.output_port.read_ints(n=2, sentinel=sentinel)
        return new_color, turn_direction


if __name__ == '__main__':
    main()
