"""
Day 5: Sunny with a Chance of Asteroids
"""
import os

from solves.day05.machine import Interaction, Machine

this_dir = os.path.dirname(os.path.abspath(__file__))
program_file = os.path.join(this_dir, "program.txt")


def read_program(file):
    with open(file) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


class PartOneInteraction(Interaction):
    def input(self) -> int:
        return 1


class PartTwoInteraction(Interaction):
    def input(self) -> int:
        return 5


def solve_part_one():
    program = read_program(program_file)
    machine = Machine(program, PartOneInteraction())
    machine.run()


def solve_part_two():
    program = read_program(program_file)
    machine = Machine(program, PartTwoInteraction())
    machine.run()


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
