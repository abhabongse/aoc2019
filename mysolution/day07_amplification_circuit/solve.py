from __future__ import annotations

import itertools
import os
import threading
from collections.abc import Sequence
from threading import Thread
from typing import NamedTuple

import more_itertools

from mysolution.machine import Machine, QueuePort, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    p1_answer = max(
        test_sequential_wiring(instructions, phases)
        for phases in itertools.permutations(range(5))
    )
    print(p1_answer)

    # Part 2
    p2_answer = max(
        test_sequential_looped_wiring(instructions, phases)
        for phases in itertools.permutations(range(5, 10))
    )
    print(p2_answer)


class Environ(NamedTuple):
    """
    Represents a pair of intcode machine
    and a thread object in which the machine executes.
    """
    machine: Machine
    thread: Thread


def test_sequential_wiring(instructions: Sequence[int], phases: Sequence[int]) -> int:
    """
    Tests the sequential wiring the series of amplifiers
    (whose intcode instructions are given),
    feed each of them the given phases settings,
    and watches for the final output signal.
    """
    # Prepare ports
    ports = [QueuePort(initial_values=[p], polling_interval=0.002) for p in phases]
    ports[0].write_int(0)
    drain = QueuePort()

    # Initializes machines and threads
    environments = []
    for input_port, output_port in more_itertools.windowed(ports + [drain], n=2):
        machine = Machine(instructions, input_port, output_port)
        thread = threading.Thread(target=machine.run_until_terminate)
        thread.start()
        environments.append(Environ(machine, thread))

    # Run until the last drain queue receives an output
    value = drain.read_int()
    for environ in environments:
        environ.machine.sigterm.set()
        environ.thread.join()

    return value


def test_sequential_looped_wiring(instructions: Sequence[int], phases: Sequence[int]) -> int:
    """
    Tests the sequential wiring the series of amplifiers (with feedback loop)
    (whose intcode instructions are given),
    feed each of them the given phases settings,
    and watches for the final output signal.
    """
    # Prepare ports
    ports = [QueuePort(initial_values=[p], polling_interval=0.002) for p in phases]
    ports[0].write_int(0)

    # Initializes I/O interfaces, programs, and threads
    environments = []
    for index, (input_port, output_port) in enumerate(more_itertools.windowed(ports + ports[:1], n=2)):
        machine = Machine(instructions, input_port, output_port)
        thread = threading.Thread(target=machine.run_until_terminate, name=f"thread-{index}")
        thread.start()
        environments.append(Environ(machine, thread))

    # Run until the last amplifier terminates
    environments[-1].thread.join()
    for environ in environments:
        environ.machine.sigterm.set()
        environ.thread.join()

    return environments[-1].machine.output_tape[-1]


if __name__ == '__main__':
    main()
