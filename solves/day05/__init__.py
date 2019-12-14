"""
Day 5: Sunny with a Chance of Asteroids
"""
import os

from solves.day05.machine import Interaction, Machine, Program

this_dir = os.path.dirname(os.path.abspath(__file__))
program_filename = os.path.join(this_dir, "program.txt")


def read_program(filename: str) -> Program:
    with open(filename) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


################
# For part one #
################

class PartOneInteraction(Interaction):
    def input(self) -> int:
        return 1  # Simulate input 1 to Intcode Program


def solve_part_one():
    program = read_program(program_filename)
    machine = Machine(program, PartOneInteraction())
    machine.run()


################
# For part two #
################

class PartTwoInteraction(Interaction):
    def input(self) -> int:
        return 5  # Simulate input 5 to Intcode Program


def solve_part_two():
    program = read_program(program_filename)
    machine = Machine(program, PartTwoInteraction())
    machine.run()


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
