from __future__ import annotations

import os
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from queue import Empty, SimpleQueue
from typing import NamedTuple

from mysolution.geometry import Vec
from mysolution.machine import Machine, Predicate, load_instructions


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    # Part 1
    start_time = time.perf_counter()
    first_vec = run_network_grid(instructions, range(50))
    p1_answer = first_vec.y
    print(p1_answer)
    print(f"first part completed in {time.perf_counter() - start_time:.3f}s")

    # Part 2
    # machine = Machine(instructions, QueuePort(script), ASCIIScreenPort())
    # machine.run_until_terminate()


@dataclass
class CentralSwitch:
    """
    Manages peer-to-peer messaging.
    """
    special_addr: int
    bridges: dict[int, BridgeAdapter] = field(default_factory=dict, init=False)
    special_output: SimpleQueue = field(default_factory=SimpleQueue, init=False)
    mutex: threading.Lock = field(default_factory=threading.Lock, init=False)

    def get_bridge(self, host_addr: int) -> BridgeAdapter:
        if host_addr not in self.bridges:
            self.bridges[host_addr] = BridgeAdapter(self, host_addr)
        return self.bridges[host_addr]

    def send_from_buffer(self, send_addr: int, buffer: Sequence[int]):
        recv_addr, x, y = buffer
        with self.mutex:
            print(f"message from [{send_addr:03}] to [{recv_addr:03}]: {x=}, {y=}")
        if recv_addr == self.special_addr:
            self.special_output.put(x)
            self.special_output.put(y)
        else:
            self.bridges[recv_addr].in_queue.put(x)
            self.bridges[recv_addr].in_queue.put(y)


@dataclass
class BridgeAdapter:
    """
    I/O port adapter from a single intcode machine towards the central switch.
    """
    switch: CentralSwitch
    addr: int
    in_queue: SimpleQueue[int] = field(default_factory=SimpleQueue, init=False)
    out_buffer: list[int] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.in_queue.put(self.addr)

    def read_int(self, sentinel: Predicate = None) -> int:
        try:
            return self.in_queue.get_nowait()
        except Empty:
            return -1

    def write_int(self, value: int, sentinel: Predicate = None):
        self.out_buffer.append(value)
        if len(self.out_buffer) == 3:
            self.switch.send_from_buffer(self.addr, self.out_buffer)
            self.out_buffer = []


class Environ(NamedTuple):
    """
    Represents a pair of intcode machine
    and a thread object in which the machine executes.
    """
    machine: Machine
    thread: threading.Thread


def run_network_grid(instructions: Sequence[int], addresses: Sequence[int]) -> Vec:
    """
    Setups intcode machines, one for each address,
    and simultaneously runs them through central switch.

    Returns the first x, y value sent to address 255.
    """
    switch = CentralSwitch(special_addr=255)
    environments = []

    for addr in addresses:
        adapter = switch.get_bridge(addr)
        machine = Machine(instructions, adapter, adapter)
        thread = threading.Thread(target=machine.run_until_terminate)
        environments.append(Environ(machine, thread))

    for environ in environments:
        environ.thread.start()

    first_x = switch.special_output.get()
    first_y = switch.special_output.get()

    for environ in environments:
        environ.machine.sigterm.set()
        environ.thread.join()

    return Vec(first_x, first_y)


if __name__ == '__main__':
    main()
