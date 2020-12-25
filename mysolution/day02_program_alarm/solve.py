from __future__ import annotations

import inspect
import itertools
import os
from collections.abc import Sequence
from dataclasses import dataclass


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    instructions = read_input_file(input_file)

    # Part 1
    program = Program.special_init(instructions, noun=12, verb=2)
    program.run_until_terminate()
    p1_answer = program.memory[0]
    print(p1_answer)

    # Part 2
    target = 19690720
    for noun, verb in itertools.product(range(100), repeat=2):
        program = Program.special_init(instructions, noun, verb)
        program.run_until_terminate()
        if program.memory[0] == target:
            print(f"{noun=} and {verb=} (output {100 * noun + verb})")


@dataclass
class Program:
    """
    Represents state of a program.
    """
    memory: list[int]
    pc: int = 0

    @classmethod
    def special_init(cls, instructions: Sequence[int], noun: int, verb: int) -> Program:
        instructions = list(instructions)
        instructions[1] = noun
        instructions[2] = verb
        return Program(instructions)

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

    def execute_01(self, fst_param, snd_param, dest_param, /):
        """
        Add two values locating at fst_param and snd_param
        and store the result at target_param.
        """
        self.memory[dest_param] = self.memory[fst_param] + self.memory[snd_param]
        self.pc += 4

    def execute_02(self, fst_param, snd_param, dest_param, /):
        """
        Add two values locating at fst_param and snd_param
        and store the result at target_param.
        """
        self.memory[dest_param] = self.memory[fst_param] * self.memory[snd_param]
        self.pc += 4

    def execute_99(self, /):
        raise ProgramTerminated


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
