from __future__ import annotations

import os

import more_itertools

from mysolution.machine import Machine, PrinterPort, QueuedPort, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    printer = PrinterPort()
    machine = Machine(instructions, QueuedPort([1]), printer)
    machine.run_until_terminate()
    p1_answer = printer.tape[-1]
    print(p1_answer)

    # Part 2
    printer = PrinterPort()
    machine = Machine(instructions, QueuedPort([5]), printer)
    machine.run_until_terminate()
    p2_answer = more_itertools.one(printer.tape)
    print(p2_answer)


if __name__ == '__main__':
    main()
