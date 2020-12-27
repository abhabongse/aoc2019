from __future__ import annotations

import itertools
import os
from collections.abc import Sequence

from mysolution.day02_program_alarm.machine import Program
from mysolution.machine import Interface, Machine, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    machine = setup_machine_with_parameters(instructions, noun=12, verb=2)
    machine.run_until_terminate()
    p1_answer = machine.memory[0]
    print(p1_answer)

    # Part 2
    target = 19690720
    for noun, verb in itertools.product(range(100), repeat=2):
        machine = Program(instructions, noun, verb)
        machine.run_until_terminate()
        if machine.memory[0] == target:
            print(f"{100 * noun + verb} ({noun=}, {verb=})")
    print("Done")


def setup_machine_with_parameters(instructions: Sequence[int], noun: int, verb: int) -> Machine:
    machine = Machine(instructions, Interface())
    machine.memory[1] = noun
    machine.memory[2] = verb
    return machine


if __name__ == '__main__':
    main()
