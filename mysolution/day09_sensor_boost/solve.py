from __future__ import annotations

import os

from mysolution.machine import Machine, PreProgrammedInterface, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    machine = Machine(instructions, PreProgrammedInterface(in_queue=[1]))
    machine.run_until_terminate()
    p1_answer = machine.interface.out_queue[-1]
    print(p1_answer)

    # Part 2
    machine = Machine(instructions, PreProgrammedInterface(in_queue=[2]))
    machine.run_until_terminate()
    p2_answer = machine.interface.out_queue[-1]
    print(p2_answer)


if __name__ == '__main__':
    main()
