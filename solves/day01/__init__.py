"""
Day 1: The Tyranny of the Rocket Equation
"""
import os
from typing import Iterator, List

this_dir = os.path.dirname(os.path.abspath(__file__))
masses_filename = os.path.join(this_dir, "masses.txt")


def read_masses(filename: str) -> List[int]:
    with open(filename) as fobj:
        return [int(line) for line in fobj]


def mass_to_fuel(mass: int) -> int:
    return mass // 3 - 2


def mass_to_compound_fuels(mass: int) -> Iterator[int]:
    fuel = mass_to_fuel(mass)
    while fuel > 0:
        yield fuel
        fuel = mass_to_fuel(fuel)


def solve_part_one():
    masses = read_masses(masses_filename)
    result = sum(mass_to_fuel(mass) for mass in masses)
    print(f"Part one: {result=}")


def solve_part_two():
    masses = read_masses(masses_filename)
    result = sum(
        sum(mass_to_compound_fuels(mass))
        for mass in masses
    )
    print(f"Part two: {result=}")


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
