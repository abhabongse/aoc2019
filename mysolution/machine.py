from __future__ import annotations

import collections
import inspect
import itertools
import sys
from collections.abc import Callable
from dataclasses import InitVar, dataclass, field
from queue import Empty, SimpleQueue
from typing import Iterator, NamedTuple, Optional, Protocol, Sequence, TextIO, runtime_checkable

Predicate = Callable[[], bool]


@dataclass
class Machine:
    """
    Implements an intcode machine which runs a given instructions.
    """
    #: Sequence of intcode instructions
    instructions: InitVar[Sequence[int]]
    #: Input port from which the machine receives an input integer
    input_port: InputPort = None
    #: Output port to which the machine sends an output integer
    output_port: OutputPort = None
    #: Flag determining whether the machine has received sigterm
    sigterm_flag: bool = field(default=False, init=False)

    #: Memory state of the machine
    memory: collections.defaultdict[int] = field(init=False)
    #: Program counter
    pc: int = field(default=0, init=False)
    #: Relative base value in conjunction with relative address mode
    relative_base: int = field(default=0, init=False)

    #: Records all input received from the input port
    input_tape: list[int] = field(default_factory=list, init=False)
    #: Records all outputs sent to the output port
    output_tape: list[int] = field(default_factory=list, init=False)

    def __post_init__(self, instructions: Sequence[int]):
        self.memory = collections.defaultdict(int, enumerate(instructions))  # noqa

    def sigterm_received(self) -> bool:
        return self.sigterm_flag

    def run_until_terminate(self):
        while not self.sigterm_flag:
            try:
                self.execute_next()
            except (MachineTerminated, ResourceUnavailable):
                break

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
        value = self.input_port.get(self.sigterm_received)
        self.store_value(dest, value)
        self.input_tape.append(value)
        self.pc += 2

    def execute_04(self, src: Parameter, /):
        """
        OUTPUT integer from `src` location.
        """
        if not self.output_port:
            raise RuntimeError("output port is not plugged")
        value = self.load_value(src)
        self.output_port.put(value, self.sigterm_received)
        self.output_tape.append(value)
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
        """
        TERMINATES the machine.
        """
        raise MachineTerminated

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

    def get(self, sentinel: Predicate = None) -> int:
        """
        An intcode machine calls this method to read an input integer.
        Once `sentinel` predicate evaluates to `True` (if provided at all),
        then this method may raise `ResourceUnavailable` if no input can be read.
        """
        raise NotImplementedError


@runtime_checkable
class OutputPort(Protocol):
    """
    Defines output port which connects an intcode machine with external output source.
    """

    def put(self, value: int, sentinel: Predicate = None):
        """
        An intcode machine calls this method to write an output integer.
        Once `sentinel` predicate evaluates to `True` (if provided at all),
        then this method may raise `ResourceUnavailable` if output cannot be written.
        """
        raise NotImplementedError


@dataclass
class KeyboardPort:
    """
    Basic input port connecting the intcode machine to the prompted standard input.
    """
    prompt: str = "Enter an input integer: "

    def get(self, _sentinel: Predicate = None) -> int:
        return int(input(self.prompt))


@dataclass
class ScreenPort:
    """
    Basic output port connecting the intcode machine to the standard output (or other stream).
    """
    prefix: str = "Integer output: "
    file: Optional[TextIO] = sys.stdout
    silent: bool = False

    def put(self, value: int, _sentinel: Predicate = None):
        if not self.silent:
            print(f"{self.prefix}{value!r}", file=self.file)


@dataclass
class QueuePort:
    """
    I/O port wrapping over `queue.SimpleQueue` for thread-safe communication.
    """
    initial_values: InitVar[Sequence[int]] = None
    queue: SimpleQueue[int] = field(init=False)
    retries: int = None
    polling_interval: float = 1.0

    def __post_init__(self, initial_values: Sequence[int] = None):
        initial_values = initial_values or []
        self.queue = SimpleQueue()
        for value in initial_values:
            self.put(value)

    def get(self, sentinel: Predicate = None) -> int:
        if self.polling_interval <= 0:
            raise ValueError("polling interval must be strictly positive")
        loop = range(self.retries) if self.retries else itertools.count()
        for _ in loop:
            try:
                return self.queue.get(timeout=self.polling_interval)
            except Empty as exc:
                if sentinel and sentinel():
                    raise ResourceUnavailable from exc
        raise ResourceUnavailable

    def put(self, value: int, _sentinel: Predicate = None):
        self.queue.put(value)


class Parameter(NamedTuple):
    number: int
    mode: int


class MachineTerminated(Exception):
    pass


class ResourceUnavailable(Exception):
    pass


def load_instructions(filename: str) -> list[int]:
    """
    Loads a list of intcode program instructions from a given filename.
    """
    with open(filename) as fobj:
        instructions = [int(token) for token in fobj.read().split(',')]
    return instructions
