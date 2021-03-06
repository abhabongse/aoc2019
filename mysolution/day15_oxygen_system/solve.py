from __future__ import annotations

import collections
import enum
import os
import sys
import threading
from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from typing import TextIO

from mysolution.geometry import Vec
from mysolution.machine import Machine, QueuePort, load_instructions

CELL_CHARS = '#.$'
DIRECTIONAL_COMMANDS = {
    Vec(0, 1): 1,
    Vec(0, -1): 2,
    Vec(-1, 0): 3,
    Vec(1, 0): 4,
}


class Status(enum.IntEnum):
    WALL = 0
    SPACE = 1
    OXYGEN = 2


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    rc_instructions = load_instructions(input_file)

    controller = DroneController(rc_instructions)
    maze_solver = MazeSolver(controller)
    maze_solver.print_area()

    # Part 1
    distances_from_origin = maze_solver.dist_from_source(Vec(0, 0))
    p1_answer = distances_from_origin[maze_solver.oxygen]
    print(p1_answer)

    # Part 2
    distances_from_oxygen = maze_solver.dist_from_source(maze_solver.oxygen)
    p2_answer = max(distances_from_oxygen.values())
    print(p2_answer)


@dataclass
class MazeSolver:
    """
    A maze solving software which interacts with the remote control (R/C) script
    (written with intcode instructions) to remotely control the repair droid.
    """
    controller: DroneController
    area: dict[Vec, Status] = field(default_factory=dict, init=False)
    oxygen: Vec = field(default=None, init=False)

    def __post_init__(self):
        with self.controller:
            self.explore_maze(pos=Vec(0, 0))

    def explore_maze(self, pos: Vec):
        """
        Recursively explores each of four possible directions.
        Part of the depth-first search (DFS) algorithm.
        """
        for step in DIRECTIONAL_COMMANDS.keys():
            if pos + step in self.area:
                continue  # already explored

            # Order the droid to move, observe the returned status,
            # and store the result
            status = self.controller.move(step)
            self.area[pos + step] = status
            if status == Status.OXYGEN:
                self.oxygen = pos + step

            # Recursively explore the maze if the droid made a move
            # and do not forget to backtrack
            if status in (Status.SPACE, Status.OXYGEN):
                self.explore_maze(pos + step)
                self.controller.move(-step)

    def dist_from_source(self, source: Vec) -> dict[Vec, int]:
        """
        Computes the shortest distance from the source to all other cells
        using breadth-first search (BFS) algorithm.
        """
        distances = {source: 0}
        queue = collections.deque([source])
        while queue:
            pos = queue.popleft()
            for step in DIRECTIONAL_COMMANDS.keys():
                if pos + step in distances or self.area[pos + step] not in (Status.SPACE, Status.OXYGEN):
                    continue
                distances[pos + step] = distances[pos] + 1
                queue.append(pos + step)
        return distances

    def print_area(self, stream: TextIO = sys.stdout):
        """
        Prints whatever is on the area to the given stream.
        """
        x_bound = range(min(p.x for p in self.area.keys()), max(p.x for p in self.area.keys()) + 1)
        y_bound = range(min(p.y for p in self.area.keys()), max(p.y for p in self.area.keys()) + 1)

        for y in reversed(y_bound):
            buffer = ''.join(self._get_cell(Vec(x, y)) for x in x_bound)
            print(buffer, file=stream)

    def _get_cell(self, pos: Vec) -> str:
        if pos == Vec(0, 0):
            return 'o'
        if pos in self.area:
            return CELL_CHARS[self.area[pos]]
        return ' '


@dataclass
class DroneController:
    """
    A remote controller script to control a droid to move according to given instructions.
    """
    rc_instructions: InitVar[Sequence[int]]
    rc_program: Machine = field(init=False)
    input_port: QueuePort = field(default_factory=QueuePort, init=False)
    output_port: QueuePort = field(default_factory=QueuePort, init=False)
    thread: threading.Thread = field(init=False)

    def __post_init__(self, rc_instructions: Sequence[int]):
        self.rc_program = Machine(rc_instructions, self.input_port, self.output_port)
        self.thread = threading.Thread(target=self.rc_program.run_until_terminate)

    def open(self):
        self.thread.start()

    def close(self):
        self.rc_program.sigterm.set()
        self.thread.join()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def move(self, step: Vec) -> Status:
        """
        Moves the drone by the provided step.
        """
        self.input_port.write_int(DIRECTIONAL_COMMANDS[step])
        return Status(self.output_port.read_int())


if __name__ == '__main__':
    main()
