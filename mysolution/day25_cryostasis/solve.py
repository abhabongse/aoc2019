from __future__ import annotations

import logging
import os
import sys
import threading
from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from typing import Optional, TextIO

import more_itertools

from mysolution.machine import Machine, OutputPort, Predicate, QueuePort, load_instructions

REJECTED_MESSAGE = b'you are ejected back to the checkpoint'

logger = logging.getLogger(__name__)


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    rc_instructions = load_instructions(input_file)

    # Part 1
    initial_commands = [
        'south', 'take cake',
        'south', 'west', 'take mutex',
        'east', 'north', 'north', 'west', 'take klein bottle',
        'south', 'east', 'take monolith',
        'south', 'take fuel cell',
        'west', 'west', 'take astrolabe',
        'east', 'east', 'north', 'west', 'north', 'west', 'north', 'take tambourine',
        'south', 'west', 'take dark matter', 'west',
    ]
    items = [item.removeprefix('take ') for item in initial_commands if item.startswith('take ')]
    # items = ['cake', 'mutex']
    controller = DroneController(rc_instructions)
    solver = Solver(controller, items, initial_commands)
    with controller:
        solver.auto_run(move_command='north')
        print("proceed")


@dataclass
class Solver:
    """
    Text-game solving software which interacts with the remote control (R/C) script
    (written with intcode instructions) to remotely control the droid.
    """
    controller: DroneController
    items: list[str]
    initial_commands: InitVar[Sequence[str]]

    def __post_init__(self, initial_commands: Sequence[str]):
        initial_commands = initial_commands or []
        for command in initial_commands:
            self.controller.append_buffer(command)

    def manual_run(self):
        """
        Manually run the solver through keyboard and screen.
        """
        while True:
            self.controller.input_port.starving.wait()
            self.controller.append_buffer(input('> '))

    def auto_run(self, move_command: str):
        """
        Automatically tries all combination of items.
        """
        last_read = 0
        previous_set = set(self.items)
        for current_set in more_itertools.powerset(self.items):
            current_set = set(current_set)
            for item in current_set - previous_set:
                self.controller.append_buffer(f'take {item}')
            for item in previous_set - current_set:
                self.controller.append_buffer(f'drop {item}')
            previous_set = current_set
            self.controller.append_buffer(move_command)
            self.controller.input_port.starving.wait()
            if REJECTED_MESSAGE not in self.controller.output_port.tape[last_read:]:
                break
            last_read = len(self.controller.output_port.tape)


@dataclass
class ASCIIScreenPort(OutputPort):
    """
    ASCII-capable screen port.
    """
    file: Optional[TextIO] = sys.stdout
    tape: bytearray = field(default_factory=bytearray, init=False)

    def write_int(self, value: int, sentinel: Predicate = None):
        self.tape.append(value)
        print(chr(value), end='', file=self.file)


@dataclass
class DroneController:
    """
    A remote controller script to control a droid to move according to given instructions.
    """
    rc_instructions: InitVar[Sequence[int]]
    rc_program: Machine = field(init=False)
    input_port: QueuePort = field(default_factory=QueuePort, init=False)
    output_port: ASCIIScreenPort = field(default_factory=ASCIIScreenPort, init=False)
    thread: threading.Thread = field(init=False)

    def __post_init__(self, rc_instructions: Sequence[int]):
        self.rc_program = Machine(rc_instructions, self.input_port, self.output_port)
        self.thread = threading.Thread(target=self.rc_program.run_until_terminate)

    def open(self):
        self.thread.start()

    def close(self):
        self.rc_program.sigterm.set()
        self.thread.join()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def append_buffer(self, text: str):
        self.input_port.write_ints(self.prepare_buffer(text))

    @classmethod
    def prepare_buffer(cls, text: str) -> list[int]:
        """
        Converts text into ASCII code integers.
        """
        return [ord(char) for char in f'{text}\n']


if __name__ == '__main__':
    main()
