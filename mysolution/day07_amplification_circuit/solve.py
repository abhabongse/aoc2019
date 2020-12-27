from __future__ import annotations

import itertools
import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from queue import Empty, SimpleQueue
from threading import Thread
from typing import NamedTuple

import more_itertools

from mysolution.machine import Interface, Machine, ProgramTerminated, load_instructions


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


@dataclass
class QueueInterface(Interface):
    """
    Thread-safe queue-based interface to intcode machine.
    """
    in_queue: SimpleQueue[int]
    out_queue: SimpleQueue[int]
    most_recent_output: int = field(init=False, default=None)
    terminated: bool = field(init=False, default=False)

    def input(self) -> int:
        while not self.terminated:
            try:
                return self.in_queue.get(timeout=0.2)
            except Empty:
                pass
        raise ProgramTerminated

    def output(self, value: int):
        self.most_recent_output = value
        self.out_queue.put(value)

    def signal_terminate(self):
        self.terminated = True


class Environ(NamedTuple):
    machine: Machine
    thread: Thread


def test_sequential_wiring(instructions: Sequence[int], phases: Sequence[int]) -> int:
    """
    Tests the sequential wiring the series of amplifiers
    (whose intcode instructions are given),
    feed each of them the given phases settings,
    and watches for the final output signal.
    """
    # Prepare queues
    queues = [SimpleQueue() for _ in phases]
    for index, phase in enumerate(phases):
        queues[index].put(phase)
    queues[0].put(0)
    drain_queue = SimpleQueue()

    # Initializes I/O interfaces, programs, and threads
    environments = []
    for in_queue, out_queue in more_itertools.windowed(queues + [drain_queue], n=2):
        machine = Machine(instructions, QueueInterface(in_queue, out_queue))
        thread = Thread(target=machine.run_until_terminate)
        thread.start()
        environments.append(Environ(machine, thread))

    # Run until the last drain queue receives an output
    value = drain_queue.get()
    for environ in environments:
        environ.machine.interface.signal_terminate()
        environ.thread.join()

    return value


def test_sequential_looped_wiring(instructions: Sequence[int], phases: Sequence[int]) -> int:
    """
    Tests the sequential wiring the series of amplifiers (with feedback loop)
    (whose intcode instructions are given),
    feed each of them the given phases settings,
    and watches for the final output signal.
    """
    # Prepare queues
    queues = [SimpleQueue() for _ in phases]
    for index, phase in enumerate(phases):
        queues[index].put(phase)
    queues[0].put(0)

    # Initializes I/O interfaces, programs, and threads
    environments = []
    for in_queue, out_queue in more_itertools.windowed(queues + queues[:1], n=2):
        machine = Machine(instructions, QueueInterface(in_queue, out_queue))
        thread = Thread(target=machine.run_until_terminate)
        thread.start()
        environments.append(Environ(machine, thread))

    # Run until the last amplifier terminates
    environments[-1].thread.join()
    for environ in environments:
        environ.machine.interface.signal_terminate()
        environ.thread.join()

    return environments[-1].machine.interface.most_recent_output


if __name__ == '__main__':
    main()
