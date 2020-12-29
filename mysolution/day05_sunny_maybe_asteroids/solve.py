from __future__ import annotations

import os

import more_itertools

from mysolution.machine import Machine, QueuePort, ScreenPort, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    machine = Machine(instructions, QueuePort(initial_values=[1]), ScreenPort())
    machine.run_until_terminate()
    p1_answer = machine.output_tape[-1]
    print(p1_answer)

    # Part 2
    machine = Machine(instructions, QueuePort(initial_values=[5]), ScreenPort(silent=True))
    machine.run_until_terminate()
    p2_answer = more_itertools.one(machine.output_tape)
    print(p2_answer)


if __name__ == '__main__':
    main()
