from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Sequence


@dataclass(init=False)
class Program:
    """
    Represents state of a program.
    """
    memory: list[int]
    pc: int = 0

    def __init__(self, instructions: Sequence[int], noun: int, verb: int):
        self.memory = list(instructions)
        self.memory[1] = noun
        self.memory[2] = verb

    def run_until_terminate(self):
        while True:
            try:
                self.execute_next()
            except ProgramTerminated:
                break

    def execute_next(self):
        instr = self.memory[self.pc]

        # Obtain the method implementing the current instruction
        method = getattr(self, f'execute_{instr:02}')
        sig = inspect.signature(method)
        nargs = sum(
            param.kind == inspect.Parameter.POSITIONAL_ONLY
            for param in sig.parameters.values()
        )

        # Prepare parameters for the method and fire!
        args = [self.memory[self.pc + 1 + pos] for pos in range(nargs)]
        method(*args)

    def execute_01(self, fst_param: int, snd_param: int, dest_param: int, /):
        """
        ADD two values locating at fst_param and snd_param
        and store the result at target_param.
        """
        self.memory[dest_param] = self.memory[fst_param] + self.memory[snd_param]
        self.pc += 4

    def execute_02(self, fst_param: int, snd_param: int, dest_param: int, /):
        """
        MULTIPLY two values locating at fst_param and snd_param
        and store the result at target_param.
        """
        self.memory[dest_param] = self.memory[fst_param] * self.memory[snd_param]
        self.pc += 4

    def execute_99(self, /):
        raise ProgramTerminated


class ProgramTerminated(Exception):
    pass
