"""
Day 1: The Tyranny of the Rocket Equation
"""
import os
from typing import Iterator, List


def read_masses(filename: str) -> List[int]:
    with open(filename) as fobj:
        return [int(line) for line in fobj]


def mass_to_fuel(mass: int) -> int:
    """
    Computes the amount of fuel required to carry the given mass.
    """
    return mass // 3 - 2


def mass_to_compound_fuels(mass: int) -> Iterator[int]:
    """
    Generates the sequence of fuels to power the given mass
    plus the recursive amount of fuel in previous step.
    """
    fuel = mass_to_fuel(mass)
    while fuel > 0:
        yield fuel
        fuel = mass_to_fuel(fuel)


def p1_sum_of_fuel_requirements(masses):
    result = sum(mass_to_fuel(mass) for mass in masses)
    print(f"Part one: {result=}")


def p2_sum_of_compounded_fuel_requirements(masses):
    result = sum(
        sum(mass_to_compound_fuels(mass))
        for mass in masses
    )
    print(f"Part two: {result=}")


if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    masses_filename = os.path.join(this_dir, "masses.txt")
    masses = read_masses(masses_filename)

    p1_sum_of_fuel_requirements(masses)
    p2_sum_of_compounded_fuel_requirements(masses)
