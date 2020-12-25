from __future__ import annotations

import inspect
import os
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import NamedTuple


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = read_input_file(input_file)

    # Part 1
    program = Program(instructions, Interface())
    print("Running program in part 1:")
    program.run_until_terminate()

    # Part 2
    program = Program(instructions, Interface())
    print("Running program in part 2:")
    program.run_until_terminate()


@dataclass(init=False)
class Program:
    """
    Represents state of a program.
    """
    memory: list[int]
    interface: Interface
    pc: int = 0

    def __init__(self, instructions: Sequence[int], interface: Interface):
        self.memory = list(instructions)
        self.interface = interface

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
        if param.mode == 0:
            return self.memory[param.number]
        elif param.mode == 1:
            return param.number
        else:
            raise RuntimeError(f"unknown mode: {param.mode!r}")

    def write_value(self, param: Parameter, value: int):
        if param.mode == 0:
            self.memory[param.number] = value
        elif param.mode == 1:
            raise RuntimeError(f"invalid mode: {param.mode!r}")
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

    def execute_99(self, /):
        raise ProgramTerminated

    @classmethod
    def _extract_modes(cls, instr: int) -> Iterator[int]:
        instr //= 100
        while True:
            yield instr % 10
            instr //= 10


class Interface:
    """
    Provides interface between intcode machine and the python world.
    """

    def input(self) -> int:
        return int(input("Enter an input integer: "))

    def output(self, value: int):
        print(f"Integer output: {value!r}")


class Parameter(NamedTuple):
    number: int
    mode: int


class ProgramTerminated(Exception):
    pass


def read_input_file(filename: str) -> list[int]:
    """
    Extracts a list of intcode program instructions.
    """
    with open(filename) as fobj:
        instructions = [
            int(token)
            for line in fobj
            for token in line.split(',')
        ]
    return instructions


if __name__ == '__main__':
    main()
