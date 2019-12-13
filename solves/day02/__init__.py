"""
Day 2: 1202 Program Alarm
"""
import os
from typing import Iterable, List

this_dir = os.path.dirname(os.path.abspath(__file__))
opcode_filename = os.path.join(this_dir, "opcode.txt")


def read_opcode(filename: str) -> List[int]:
    with open(filename) as fobj:
        return [int(token) for token in fobj.read().split(",")]


def run_intcode_program(program: Iterable[int], noun: int, verb: int):
    memory = list(program)
    memory[1] = noun
    memory[2] = verb
    pc = 0

    while True:
        if memory[pc] == 1:
            # Addition
            fst = memory[memory[pc + 1]]
            snd = memory[memory[pc + 2]]
            memory[memory[pc + 3]] = fst + snd
            pc += 4
        elif memory[pc] == 2:
            # Multiplication
            fst = memory[memory[pc + 1]]
            snd = memory[memory[pc + 2]]
            memory[memory[pc + 3]] = fst * snd
            pc += 4
        elif memory[pc] == 99:
            # Halt
            return memory[0]
        else:
            raise RuntimeError


def solve_part_one():
    opcode = read_opcode(opcode_filename)
    result = run_intcode_program(opcode, 12, 2)
    print(f"Part one: {result=}")


def solve_part_two():
    opcode = read_opcode(opcode_filename)
    target = 19690720
    for noun in range(100):
        for verb in range(100):
            if run_intcode_program(opcode, noun, verb) == target:
                print(f'Matched: {noun=}, {verb=}')


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
