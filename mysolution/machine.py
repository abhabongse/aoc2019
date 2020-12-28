from __future__ import annotations

import collections
import inspect
import sys
import threading
from dataclasses import InitVar, dataclass, field
from typing import Generic, Iterator, NamedTuple, Optional, Protocol, Sequence, TextIO, runtime_checkable


@dataclass
class Machine:
    """
    Implements an intcode machine which runs a program
    (i.e. a given list of instructions).
    """
    memory: collections.defaultdict[int] = field(init=False)
    instructions: InitVar[Sequence[int]]
    input_port: InputPort = None
    output_port: OutputPort = None
    pc: int = field(default=0, init=False)
    relative_base: int = field(default=0, init=False)
    sigterm_received: bool = field(default=False, init=False)

    def __post_init__(self, instructions: Sequence[int]):
        self.memory = collections.defaultdict(int, enumerate(instructions))  # noqa

    def send_sigterm(self):
        self.sigterm_received = True
        if self.input_port:
            self.input_port.notify_sigterm()
        if self.output_port:
            self.output_port.notify_sigterm()

    def run_until_terminate(self):
        while not self.sigterm_received:
            try:
                self.execute_next()
            except ProcessTerminated:
                break
        self.send_sigterm()

    def execute_next(self):
        instr = self.memory[self.pc]

        # Obtain the method implementing the current instruction
        method = getattr(self, f'execute_{instr % 100:02}')
        sig = inspect.signature(method)
        nargs = sum(
            param.kind == inspect.Parameter.POSITIONAL_ONLY
            for param in sig.parameters.values()
        )

        # Prepare parameters for the method and fire!
        args = [
            Parameter(self.memory[self.pc + 1 + pos], mode)
            for pos, mode in zip(range(nargs), self._extract_modes(instr))
        ]
        method(*args)

    def load_value(self, param: Parameter):
        if param.mode == 0:  # absolute address mode
            return self.memory[param.number]
        elif param.mode == 1:  # immediate mode
            return param.number
        elif param.mode == 2:  # relative address mode
            return self.memory[param.number + self.relative_base]
        else:
            raise RuntimeError(f"unknown mode: {param.mode!r}")

    def store_value(self, param: Parameter, value: int):
        if param.mode == 0:  # absolute address mode
            self.memory[param.number] = value
        elif param.mode == 1:  # immediate mode
            raise RuntimeError(f"invalid mode: {param.mode!r}")
        elif param.mode == 2:  # relative address mode
            self.memory[param.number + self.relative_base] = value
        else:
            raise RuntimeError(f"unknown mode: {param.mode!r}")

    def execute_01(self, fst: Parameter, snd: Parameter, dest: Parameter, /):
        """
        ADD two values from `fst` and `snd` params and store at `dest`.
        Statement: `dest = fst + snd`
        """
        fst_value = self.load_value(fst)
        snd_value = self.load_value(snd)
        self.store_value(dest, fst_value + snd_value)
        self.pc += 4

    def execute_02(self, fst: Parameter, snd: Parameter, dest: Parameter, /):
        """
        MULTIPLY two values from `fst` and `snd` params and store at `dest`.
        Statement: `dest = fst * snd`
        """
        fst_value = self.load_value(fst)
        snd_value = self.load_value(snd)
        self.store_value(dest, fst_value * snd_value)
        self.pc += 4

    def execute_03(self, dest: Parameter, /):
        """
        Saves INPUT integer to `dest`.
        """
        if not self.input_port:
            raise RuntimeError("input port is not plugged")
        value = self.input_port.get()
        self.store_value(dest, value)
        self.pc += 2

    def execute_04(self, src: Parameter, /):
        """
        OUTPUT integer from `src` location.
        """
        if not self.output_port:
            raise RuntimeError("output port is not plugged")
        value = self.load_value(src)
        self.output_port.put(value)
        self.pc += 2

    def execute_05(self, cond: Parameter, pos: Parameter, /):
        """
        If `cond` is non-zero, then jump pc to `pos`.
        JUMP_IF_TRUE branching instruction.
        """
        cond_value = self.load_value(cond)
        pos_value = self.load_value(pos)
        self.pc = pos_value if cond_value else self.pc + 3

    def execute_06(self, cond: Parameter, pos: Parameter, /):
        """
        If `cond` is zero, then jump pc to `pos`.
        JUMP_IF_FALSE branching instruction.
        """
        cond_value = self.load_value(cond)
        pos_value = self.load_value(pos)
        self.pc = pos_value if not cond_value else self.pc + 3

    def execute_07(self, fst: Parameter, snd: Parameter, dest: Parameter, /):
        """
        Compares whether `fst` is strictly LESS THAN `snd`.
        Statement: `dest = (fst < snd) ? 1 : 0`
        """
        fst_value = self.load_value(fst)
        snd_value = self.load_value(snd)
        self.store_value(dest, int(fst_value < snd_value))
        self.pc += 4

    def execute_08(self, fst: Parameter, snd: Parameter, dest: Parameter, /):
        """
        Compares whether `fst` and `snd` are EQUAL.
        Statement: `dest = (fst == snd) ? 1 : 0`
        """
        fst_value = self.load_value(fst)
        snd_value = self.load_value(snd)
        self.store_value(dest, int(fst_value == snd_value))
        self.pc += 4

    def execute_09(self, adjust: Parameter, /):
        """
        ADJUSTS the RELATIVE BASE of the relative position mode.
        """
        adjust_value = self.load_value(adjust)
        self.relative_base += adjust_value
        self.pc += 2

    def execute_99(self, /):
        raise ProcessTerminated

    @classmethod
    def _extract_modes(cls, instr: int) -> Iterator[int]:
        instr //= 100
        while True:
            yield instr % 10
            instr //= 10


@runtime_checkable
class InputPort(Protocol):
    """
    Defines input port which connects an intcode machine with external input source.
    """

    def get(self) -> int:
        """
        An intcode machine calls this method to read an input.
        """
        ...

    def notify_sigterm(self):
        """
        An intcode machine calls this method to let the port know of the sigterm.
        """
        ...


@runtime_checkable
class OutputPort(Protocol):
    """
    Defines input port which connects an intcode machine with external input source.
    """

    def put(self, value: int):
        """
        An intcode machine calls this method to write an output.
        """
        ...

    def notify_sigterm(self):
        """
        An intcode machine calls this method to let the port know of the sigterm.
        """
        ...


@dataclass
class PrompterPort:
    """
    Basic input port connecting to the prompted standard input.
    """
    prompt: str = "Enter an input integer: "
    tape: list[int] = field(default_factory=list, init=False)

    def get(self) -> int:
        value = int(input(self.prompt))
        self.tape.append(value)
        return value

    def notify_sigterm(self):
        pass


@dataclass
class PrinterPort:
    """
    Basic output port connecting to the standard output (or other file object).
    """
    print_prefix: str = None
    file: Optional[TextIO] = sys.stdout
    tape: list[int] = field(default_factory=list, init=False)

    def put(self, value: int):
        self.tape.append(value)
        if self.print_prefix is not None:
            print(f"{self.print_prefix}{value!r}")

    def notify_sigterm(self):
        pass


@dataclass
class QueuedPort:
    """
    I/O port connecting an intcode machine with thread-safe queue.
    """
    initial_values: InitVar[Sequence[int]] = None
    queue: collections.deque[int] = field(default_factory=collections.deque)
    tape: list[int] = field(init=False)
    sigterm_received: bool = field(init=False)
    mutex: threading.Lock = field(init=False)
    not_empty: threading.Condition = field(init=False)

    def __post_init__(self, initial_values: Sequence[int] = None):
        self.queue.extend(initial_values or [])
        self.tape = list(self.queue)
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.sigterm_received = False

    def get(self) -> int:
        with self.not_empty:
            while not self.queue and not self.sigterm_received:
                self.not_empty.wait()
            if self.sigterm_received:
                raise ProcessTerminated
            return self.queue.popleft()

    def put(self, value: int):
        with self.mutex:
            self.tape.append(value)
            self.queue.append(value)
            self.not_empty.notify()

    def notify_sigterm(self):
        self.sigterm_received = True


class Parameter(NamedTuple):
    number: int
    mode: int


class ProcessTerminated(Exception):
    pass


def load_instructions(filename: str) -> list[int]:
    """
    Loads a list of intcode program instructions from a given filename.
    """
    with open(filename) as fobj:
        instructions = [int(token) for token in fobj.read().split(',')]
    return instructions
