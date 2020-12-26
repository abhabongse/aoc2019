from __future__ import annotations

import itertools
import os

from mysolution.day02_program_alarm.machine import Program


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = read_input_file(input_file)

    # Part 1
    program = Program(instructions, noun=12, verb=2)
    program.run_until_terminate()
    p1_answer = program.memory[0]
    print(p1_answer)

    # Part 2
    target = 19690720
    for noun, verb in itertools.product(range(100), repeat=2):
        program = Program(instructions, noun, verb)
        program.run_until_terminate()
        if program.memory[0] == target:
            print(f"{noun=} and {verb=} (output {100 * noun + verb})")


def read_input_file(filename: str) -> list[int]:
    """
    Extracts a list of intcode program instructions.
    """
    with open(filename) as fobj:
        instructions = [int(token) for token in fobj.read().split(',')]
    return instructions


if __name__ == '__main__':
    main()
