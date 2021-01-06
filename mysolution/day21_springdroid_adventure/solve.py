from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional, TextIO

from mysolution.machine import Machine, OutputPort, Predicate, QueuePort, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # IMPORTANT NOTE:
    # I really don't like today's problem.
    # The problem statement is unclear of what kind of behavior the droid makes
    # and the problem is intractable in general case anyway.

    # Part 1
    script = prepare_springscript([
        'OR A J',
        'AND B J',
        'AND C J',
        'NOT J J',
        'AND D J',
        'WALK',
    ])
    machine = Machine(instructions, QueuePort(script), ASCIIScreenPort())
    machine.run_until_terminate()

    # Part 2
    script = prepare_springscript([
        'OR A J',
        'AND B J',
        'AND C J',
        'NOT J J',
        'AND D J',
        'OR E T',
        'OR H T',
        'AND T J',
        'RUN',
    ])
    machine = Machine(instructions, QueuePort(script), ASCIIScreenPort())
    machine.run_until_terminate()


def prepare_springscript(script: Sequence[str]) -> list[int]:
    """
    Prepare springscript in the form accepted by ASCII-capable port.
    """
    serialized_input = [
        ord(char)
        for line in script
        for char in f'{line}\n'
    ]
    return serialized_input


@dataclass
class ASCIIScreenPort(OutputPort):
    """
    ASCII-capable screen port.
    """
    file: Optional[TextIO] = sys.stdout

    def write_int(self, value: int, sentinel: Predicate = None):
        if value >= 128:
            print(">", value, file=self.file)
        else:
            print(chr(value), end='', file=self.file)


if __name__ == '__main__':
    main()
