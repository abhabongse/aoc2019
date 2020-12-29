from __future__ import annotations

import itertools
import os
from collections.abc import Sequence

from mysolution.machine import Machine, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    machine = setup_machine(instructions, noun=12, verb=2)
    machine.run_until_terminate()
    p1_answer = machine.memory[0]
    print(p1_answer)

    # Part 2
    target = 19690720
    for noun, verb in itertools.product(range(100), repeat=2):
        machine = setup_machine(instructions, noun, verb)
        machine.run_until_terminate()
        if machine.memory[0] == target:
            print(f"{100 * noun + verb} ({noun=}, {verb=})")


def setup_machine(instructions: Sequence[int], noun: int, verb: int) -> Machine:
    """
    Setup intcode machine with the given instructions,
    replacing the noun and verb parameters with the given values.
    """
    machine = Machine(instructions)
    machine.memory[1] = noun
    machine.memory[2] = verb
    return machine


if __name__ == '__main__':
    main()
