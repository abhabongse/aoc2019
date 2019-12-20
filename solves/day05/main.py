"""
Day 5: Sunny with a Chance of Asteroids
"""
import os

from solves.day05.machine import Interaction, Machine, Program


def read_opcode(filename: str) -> Program:
    with open(filename) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


class DiagnosticInteraction(Interaction):
    input_signal: int
    count: int

    def __init__(self, input_value: int):
        self.input_signal = input_value
        self.count = 0

    def input(self) -> int:
        if self.count == 1:
            raise RuntimeError
        self.count += 1
        # Simulate input to Intcode Program
        return self.input_signal


def p1_system_id_1(diagnostic_program: Program):
    machine = Machine(diagnostic_program, DiagnosticInteraction(1))
    machine.run()


def p2_system_id_5(diagnostic_program: Program):
    machine = Machine(diagnostic_program, DiagnosticInteraction(5))
    machine.run()


if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    diagnostic_opcode_filename = os.path.join(this_dir, "diagnostic.txt")
    diagnostic_program = read_opcode(diagnostic_opcode_filename)

    p1_system_id_1(diagnostic_program)
    p2_system_id_5(diagnostic_program)
