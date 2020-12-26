from __future__ import annotations

import collections
import os
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

from mysolution.day09_sensor_boost.machine import Interface, Program

T = TypeVar('T')


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = read_input_file(input_file)

    # Part 1
    interface = AutomatedInterface([1])
    program = Program(instructions, interface)
    program.run_until_terminate()
    p1_answer = interface.out_queue[-1]
    print(p1_answer)

    # Part 2
    interface = AutomatedInterface([2])
    program = Program(instructions, interface)
    program.run_until_terminate()
    p2_answer = interface.out_queue[-1]
    print(p2_answer)


@dataclass(init=False)
class AutomatedInterface(Interface):
    """
    Thread-safe queue-based interface to intcode machine.
    """
    in_queue: collections.deque[int]
    out_queue: collections.deque[int]

    def __init__(self, in_queue: Sequence[int] = None, out_queue: Sequence[int] = None):
        self.in_queue = collections.deque(in_queue or [])
        self.out_queue = collections.deque(out_queue or [])

    def input(self) -> int:
        value = self.in_queue.popleft()
        return value

    def output(self, value: int):
        self.out_queue.append(value)


def read_input_file(filename: str) -> list[int]:
    """
    Extracts a list of intcode program instructions.
    """
    with open(filename) as fobj:
        instructions = [
            int(token)
            for line in fobj
            for token in line.split(',')
        ]
    return instructions


if __name__ == '__main__':
    main()
