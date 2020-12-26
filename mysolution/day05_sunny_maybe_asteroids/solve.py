from __future__ import annotations

import os

from mysolution.day05_sunny_maybe_asteroids.machine import Interface, Program


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = read_input_file(input_file)

    # Part 1
    program = Program(instructions, Interface())
    print("Running program in part 1:")
    program.run_until_terminate()

    # Part 2
    program = Program(instructions, Interface())
    print("Running program in part 2:")
    program.run_until_terminate()


def read_input_file(filename: str) -> list[int]:
    """
    Extracts a list of intcode program instructions.
    """
    with open(filename) as fobj:
        instructions = [int(token) for token in fobj.read().split(',')]
    return instructions


if __name__ == '__main__':
    main()
