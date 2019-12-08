"""
Day 1: The Tyranny of the Rocket Equation
"""
import os

this_dir = os.path.dirname(os.path.abspath(__file__))
masses_file = os.path.join(this_dir, "masses.txt")


def read_masses(file):
    with open(file) as fobj:
        return [int(line) for line in fobj]


def mass_to_fuel(mass):
    return mass // 3 - 2


def mass_to_compound_fuels(mass):
    fuel = mass_to_fuel(mass)
    while fuel > 0:
        yield fuel
        fuel = mass_to_fuel(fuel)


def solve_part_one():
    masses = read_masses(masses_file)
    result = sum(mass_to_fuel(mass) for mass in masses)
    print(result)


def solve_part_two():
    masses = read_masses(masses_file)
    result = sum(sum(mass_to_compound_fuels(mass)) for mass in masses)
    print(result)


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
