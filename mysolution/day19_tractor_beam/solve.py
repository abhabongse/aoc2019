from __future__ import annotations

import itertools
import os
import threading
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TypeVar

import more_itertools
from tqdm import tqdm, trange

from mysolution.machine import Machine, QueuePort, load_instructions

T = TypeVar('T')


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    rc_instructions = load_instructions(input_file)

    # Part 1
    controller = DroneController(rc_instructions)
    p1_answer = probe_rectangle(controller, width=50, height=50)
    print(p1_answer)

    # Part 2
    scanner = RectangleScanner(controller, width=100, height=100)
    p2_answer = f"{scanner.head_x * 10000 + scanner.head_y}"
    print(p2_answer)


def probe_rectangle(controller: DroneController, width: int, height: int) -> int:
    """
    Probe a given rectangular area [0, width) × [0, height).
    """
    total = 0
    with trange(height) as pbar:
        for y in pbar:
            output_buffer = [controller.probe(x, y) for x in range(width)]
            total += sum(output_buffer)
            pbar.write(''.join('#' if c else '.' for c in output_buffer))
    return total


@dataclass
class RectangleScanner:
    controller: DroneController
    width: int
    height: int

    head_x: int = field(init=False)
    head_y: int = field(init=False)
    falloff_x: int = field(init=False)
    falloff_y: int = field(init=False)

    def __post_init__(self):
        self.scan_for_rectangle()

    def scan_for_rectangle(self):
        """
        Scans for the top-left position of a rectangle of the given dimensions
        contained within the beam nearest to the origin.
        """
        self.head_x, self.head_y = self.scan_for_starting_position()
        self.falloff_x, self.falloff_y = self.head_x, self.head_y
        self._update_falloff_x()
        self._update_falloff_y()

        with tqdm(total=self.width + self.height) as pbar:
            pbar.update(self._progress)
            while self._accm_width < self.width or self._accm_height < self.height:
                while self._accm_width < self.width and self.head_y + 1 < self.falloff_y:
                    self.head_y += 1
                    self._update_falloff_x()
                    pbar.update(self._progress - pbar.n)
                    # pbar.set_description("")
                while self._accm_height < self.height and self.head_x + 1 < self.falloff_x:
                    self.head_x += 1
                    self._update_falloff_y()
                    pbar.update(self._progress - pbar.n)

    def scan_for_starting_position(self) -> tuple[int, int]:
        """
        Scans for the top-left position of a 2×2 square
        contained within the beam nearest to the origin.
        """
        caches = {(0, 0): self.controller.probe(0, 0)}
        for side in itertools.count():
            for col in range(side + 2):
                caches[col, side + 1] = self.controller.probe(col, side + 1)
            for row in range(side + 2):
                caches[side + 1, row] = self.controller.probe(side + 1, row)
            for col in range(side):
                if all(caches[col + dx, side + dy] for dx, dy in itertools.product(range(2), repeat=2)):
                    return col, side
            for row in range(side):
                if all(caches[side + dx, row + dy] for dx, dy in itertools.product(range(2), repeat=2)):
                    return side, row

    @property
    def _accm_width(self) -> int:
        return self.falloff_x - self.head_x

    @property
    def _accm_height(self) -> int:
        return self.falloff_y - self.head_y

    @property
    def _progress(self) -> int:
        return self._accm_width + self._accm_height

    def _update_falloff_x(self):
        self.falloff_x = more_itertools.first_true(
            itertools.count(start=self.falloff_x),
            pred=lambda x: not self.controller.probe(x, self.head_y),
        )

    def _update_falloff_y(self):
        self.falloff_y = more_itertools.first_true(
            itertools.count(start=self.falloff_y),
            pred=lambda y: not self.controller.probe(self.head_x, y),
        )


@dataclass(init=False)
class DroneController:
    """
    A remote controller (R/C) script to deploy a drone to a particular location
    and see it is stationery or gets pulled by *something*. Spooky.
    """
    rc_instructions: list[int]

    def __init__(self, rc_instructions: Sequence[int]):
        self.rc_instructions = list(rc_instructions)

    def probe(self, x: int, y: int) -> int:
        """
        Deploys a drone to the given position and observe the result.
        This function returns 0 if the drone is stationery
        or returns 1 if it gets pulled by something.
        """
        input_port = QueuePort()
        output_port = QueuePort()
        rc_program = Machine(self.rc_instructions, input_port, output_port)

        thread = threading.Thread(target=rc_program.run_until_terminate)
        thread.start()
        input_port.write_int(x)
        input_port.write_int(y)
        thread.join()

        return output_port.read_int()


if __name__ == '__main__':
    main()
