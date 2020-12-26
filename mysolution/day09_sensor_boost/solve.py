from __future__ import annotations

import os
from typing import TypeVar

from mysolution.day09_sensor_boost.machine import AutomatedInterface, Program

T = TypeVar('T')


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = read_input_file(input_file)

    # Part 1
    interface = AutomatedInterface(in_queue=[1])
    program = Program(instructions, interface)
    program.run_until_terminate()
    p1_answer = interface.out_queue[-1]
    print(p1_answer)

    # Part 2
    interface = AutomatedInterface(in_queue=[2])
    program = Program(instructions, interface)
    program.run_until_terminate()
    p2_answer = interface.out_queue[-1]
    print(p2_answer)


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
