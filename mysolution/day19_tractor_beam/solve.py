from __future__ import annotations

import os
import threading
from collections.abc import Sequence
from dataclasses import dataclass

from tqdm import trange

from mysolution.machine import Machine, QueuePort, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    rc_instructions = load_instructions(input_file)

    # Part 1
    controller = DroneController(rc_instructions)
    p1_answer = probe_area(controller, width=50, height=50)
    print(p1_answer)

    # Part 2
    p2_answer = ...
    print(p2_answer)


def probe_area(controller: DroneController, width: int, height: int) -> int:
    """
    Probe a given rectangular area [0, width) × [0, height).
    """
    total = 0
    with trange(height) as pbar:
        for y in pbar:
            output_buffer = [controller.probe_position(x, y) for x in range(width)]
            total += sum(output_buffer)
            pbar.write(''.join('#' if c else '.' for c in output_buffer))
    return total


@dataclass(init=False)
class DroneController:
    """
    A remote controller to deploy a drone to a particular location
    and see it is stationery or gets pulled by *something*. Spooky.
    """
    rc_instructions: list[int]

    def __init__(self, rc_instructions: Sequence[int]):
        self.rc_instructions = list(rc_instructions)

    def probe_position(self, x: int, y: int) -> int:
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
