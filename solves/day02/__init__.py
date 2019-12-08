"""
Day 2: 1202 Program Alarm
"""
import os

this_dir = os.path.dirname(os.path.abspath(__file__))
opcode_file = os.path.join(this_dir, "program.txt")

test_cases = [
    [1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
    [1, 0, 0, 0, 99],
    [2, 3, 0, 3, 99],
    [2, 4, 4, 5, 99, 0],
    [1, 1, 1, 4, 99, 5, 6, 0, 99],
]


def read_opcode(file):
    with open(file) as fobj:
        return [int(token) for token in fobj.read().split(",")]


def run_program(program, noun, verb):
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
    opcode = read_opcode(opcode_file)
    result = run_program(opcode, 12, 2)
    print(result)


def solve_part_two():
    opcode = read_opcode(opcode_file)
    target = 19690720
    for noun in range(100):
        for verb in range(100):
            if run_program(opcode, noun, verb) == target:
                print(f'{noun=}, {verb=}')


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
    # print(run_program(test_cases[0]))
