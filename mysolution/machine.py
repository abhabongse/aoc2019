from __future__ import annotations

import collections
import inspect
from dataclasses import dataclass
from typing import Iterator, NamedTuple, Sequence, TypeVar

InterfaceType = TypeVar('InterfaceType', bound='Interface')


@dataclass(init=False)
class Machine:
    """
    Implements an intcode machine which runs a program
    (i.e. a given list of instructions).
    """
    memory: list[int]
    interface: InterfaceType
    pc: int
    relative_base: int

    def __init__(self, instructions: Sequence[int], interface: InterfaceType):
        self.memory = collections.defaultdict(int, enumerate(instructions))  # noqa
        self.interface = interface
        self.pc = 0
        self.relative_base = 0

    def run_until_terminate(self):
        while True:
            try:
                self.execute_next()
            except ProgramTerminated:
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

    def read_value(self, param: Parameter):
        if param.mode == 0:  # absolute address mode
            return self.memory[param.number]
        elif param.mode == 1:  # immediate mode
            return param.number
        elif param.mode == 2:  # relative address mode
            return self.memory[param.number + self.relative_base]
        else:
            raise RuntimeError(f"unknown mode: {param.mode!r}")

    def write_value(self, param: Parameter, value: int):
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
        fst_value = self.read_value(fst)
        snd_value = self.read_value(snd)
        self.write_value(dest, fst_value + snd_value)
        self.pc += 4

    def execute_02(self, fst: Parameter, snd: Parameter, dest: Parameter, /):
        """
        MULTIPLY two values from `fst` and `snd` params and store at `dest`.
        Statement: `dest = fst * snd`
        """
        fst_value = self.read_value(fst)
        snd_value = self.read_value(snd)
        self.write_value(dest, fst_value * snd_value)
        self.pc += 4

    def execute_03(self, dest: Parameter, /):
        """
        Saves INPUT integer to `dest`.
        """
        value = self.interface.input()
        self.write_value(dest, value)
        self.pc += 2

    def execute_04(self, src: Parameter, /):
        """
        OUTPUT integer from `src` location.
        """
        value = self.read_value(src)
        self.interface.output(value)
        self.pc += 2

    def execute_05(self, cond: Parameter, pos: Parameter, /):
        """
        If `cond` is non-zero, then jump pc to `pos`.
        JUMP_IF_TRUE branching instruction.
        """
        cond_value = self.read_value(cond)
        pos_value = self.read_value(pos)
        self.pc = pos_value if cond_value else self.pc + 3

    def execute_06(self, cond: Parameter, pos: Parameter, /):
        """
        If `cond` is zero, then jump pc to `pos`.
        JUMP_IF_FALSE branching instruction.
        """
        cond_value = self.read_value(cond)
        pos_value = self.read_value(pos)
        self.pc = pos_value if not cond_value else self.pc + 3

    def execute_07(self, fst: Parameter, snd: Parameter, dest: Parameter, /):
        """
        Compares whether `fst` is strictly LESS THAN `snd`.
        Statement: `dest = (fst < snd) ? 1 : 0`
        """
        fst_value = self.read_value(fst)
        snd_value = self.read_value(snd)
        self.write_value(dest, int(fst_value < snd_value))
        self.pc += 4

    def execute_08(self, fst: Parameter, snd: Parameter, dest: Parameter, /):
        """
        Compares whether `fst` and `snd` are EQUAL.
        Statement: `dest = (fst == snd) ? 1 : 0`
        """
        fst_value = self.read_value(fst)
        snd_value = self.read_value(snd)
        self.write_value(dest, int(fst_value == snd_value))
        self.pc += 4

    def execute_09(self, adjust: Parameter, /):
        """
        ADJUSTS the RELATIVE BASE of the relative position mode.
        """
        adjust_value = self.read_value(adjust)
        self.relative_base += adjust_value
        self.pc += 2

    def execute_99(self, /):
        raise ProgramTerminated

    @classmethod
    def _extract_modes(cls, instr: int) -> Iterator[int]:
        instr //= 100
        while True:
            yield instr % 10
            instr //= 10


@dataclass
class Interface:
    """
    Provides interface between intcode machine and the python world.
    """

    def input(self) -> int:
        return int(input("Enter an input integer: "))

    def output(self, value: int):
        print(f"Integer output: {value!r}")


@dataclass(init=False)
class PreProgrammedInterface(Interface):
    """
    Thread-safe queue-based interface to intcode machine.
    """
    in_queue: collections.deque[int]
    out_queue: collections.deque[int]

    def __init__(self, in_queue: Sequence[int] = None):
        self.in_queue = collections.deque(in_queue or [])
        self.out_queue = collections.deque()

    def input(self) -> int:
        value = self.in_queue.popleft()
        return value

    def output(self, value: int):
        self.out_queue.append(value)


class Parameter(NamedTuple):
    number: int
    mode: int


class ProgramTerminated(Exception):
    pass


def load_instructions(filename: str) -> list[int]:
    """
    Loads a list of intcode program instructions from a given filename.
    """
    with open(filename) as fobj:
        instructions = [int(token) for token in fobj.read().split(',')]
    return instructions
