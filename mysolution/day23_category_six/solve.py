from __future__ import annotations

import collections
import logging
import os
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import NamedTuple

from mysolution.geometry import Vec
from mysolution.machine import InputPort, Machine, OutputPort, Predicate, load_instructions

logger = logging.getLogger(__name__)


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = load_instructions(input_file)

    logging.basicConfig(
        format='%(threadName)s %(levelname)5s %(relativeCreated)5d: %(message)s',
        level=logging.DEBUG,
    )
    start_time = time.perf_counter()

    # Setup all intcode machine with their respective addresses
    switch = CentralSwitch()
    environments = []
    for addr in range(50):
        adapter = switch.get_bridge(addr)
        machine = Machine(instructions, adapter, adapter)
        thread = threading.Thread(target=machine.run_until_terminate, name=f"machine-{addr:02}")
        environments.append(Environ(machine, thread))

    # Start up all machines
    for environ in environments:
        environ.thread.start()

    # Wait until NAT receives the first message
    switch.nat_first_received.wait()
    p1_answer = switch.nat_received_msgs[0].y
    print(p1_answer)
    logger.info(f"part 1 done in {time.perf_counter() - start_time}s since beginning")

    # Start up NAT and run until first Y repeat
    switch.nat_run_until_send_repeated()
    p2_answer = switch.nat_sent_msgs[-1].y
    print(p2_answer)
    logger.info(f"part 2 done in {time.perf_counter() - start_time}s since beginning")

    # Clean up threads
    for environ in environments:
        environ.machine.sigterm.set()
        environ.thread.join()


class Environ(NamedTuple):
    """
    Represents a pair of intcode machine
    and a thread object in which the machine executes.
    """
    machine: Machine
    thread: threading.Thread


@dataclass
class CentralSwitch:
    """
    A centralized controller which manages the peer-to-peer messaging
    between intcode machines with each other and with NAT.
    """
    nat_addr: int = 255
    bridges: dict[int, BridgeAdapter] = field(default_factory=dict, init=False)

    mutex: threading.Lock = field(default_factory=threading.Lock, init=False)
    nat_first_received: threading.Event = field(default_factory=threading.Event, init=False)
    nat_received_msgs: collections.deque[Vec] = field(default_factory=collections.deque, init=False)
    nat_sent_msgs: collections.deque[Vec] = field(default_factory=collections.deque, init=False)

    def __post_init__(self):
        self.idle_mutex = threading.RLock()
        self.idling = threading.Condition(lock=self.idle_mutex)

    def get_bridge(self, host_addr: int) -> BridgeAdapter:
        """
        Creates a new bridge adapter with the given host address.
        """
        if host_addr == self.nat_addr:
            raise ValueError(f"unacceptable machine address: {host_addr}")
        if host_addr not in self.bridges:
            self.bridges[host_addr] = BridgeAdapter(self, host_addr)
        return self.bridges[host_addr]

    def dispatch_buffer(self, send_addr: int, buffer: Sequence[int]):
        """
        Extracts information from the given output buffer
        and delivers the message to the appropriate destination (either a machine or NAT).
        """
        recv_addr, x, y = buffer
        self.log_msg(send_addr, recv_addr, x, y)
        if recv_addr == self.nat_addr:
            self.nat_received_msgs.append(Vec(x, y))
            self.nat_first_received.set()
        else:
            self.deliver_to_machine(recv_addr, x, y)

    def deliver_to_machine(self, addr: int, x: int, y: int):
        """
        Delivers the message to a machine at the given address.
        Sends the message to the given receiver address.
        """
        adapter = self.bridges[addr]
        adapter.in_queue.extend([x, y])
        with self.mutex:
            adapter.in_starving.clear()

    def nat_run_until_send_repeated(self):
        """
        Runs the NAT until the first consecutive repeat of the Y-message
        would about to be sent to the machine at address 0.
        """
        while True:
            if not self.network_idle():
                for adapter in self.bridges.values():
                    adapter.in_starving.wait()
                continue
            recent_msg = self.nat_received_msgs[-1]
            if self.nat_sent_msgs and self.nat_sent_msgs[-1].y == recent_msg.y:
                return  # found a repeat
            self.nat_sent_msgs.append(recent_msg)
            self.deliver_to_machine(0, recent_msg.x, recent_msg.y)
            self.log_msg(self.nat_addr, 0, recent_msg.x, recent_msg.y)

    def network_idle(self) -> bool:
        """
        Determines whether the entire network is considered idle:
        that is whether each machine is idle (constantly waiting for input)
        AND there is no message waiting in any queue.
        """
        with self.mutex:
            return all(adapter.in_starving.is_set() for adapter in self.bridges.values())

    def log_msg(self, send_addr: int, recv_addr: int, x: int, y: int):
        """
        Uses logging module to log the messages passing through
        from the given sender to the given receiver.
        """
        send_addr = 'NAT' if send_addr == self.nat_addr else f'{send_addr:03}'
        recv_addr = 'NAT' if recv_addr == self.nat_addr else f'{recv_addr:03}'
        logger.debug(f"msg from [{send_addr}] to [{recv_addr}]: {x=}, {y=}")


@dataclass
class BridgeAdapter(InputPort, OutputPort):
    """
    I/O port wrapping over `queue.SimpleQueue` for thread-safe communication.
    """
    switch: CentralSwitch
    addr: int
    polling_interval: float = 0.1
    in_queue: collections.deque[int] = field(default_factory=collections.deque, init=False)
    out_buffer: list[int] = field(default_factory=list, init=False)
    in_starving: threading.Event = field(default_factory=threading.Event, init=False)

    def __post_init__(self):
        self.in_queue.append(self.addr)

    def read_int(self, sentinel: Predicate = None) -> int:
        if self.in_queue:
            return self.in_queue.popleft()
        self.in_starving.set()
        time.sleep(self.polling_interval)
        return -1

    def write_int(self, value: int, sentinel: Predicate = None):
        self.out_buffer.append(value)
        if len(self.out_buffer) == 3:
            self.switch.dispatch_buffer(self.addr, self.out_buffer)
            self.out_buffer = []


if __name__ == '__main__':
    main()
