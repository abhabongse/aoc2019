"""
Day 4: Secure Container
"""

#########
# Input #
#########

lower = 271973
upper = 785961


#############
# Functions #
#############

def fits_criteria(number: int) -> bool:
    digits = str(number)
    return (len(digits) == 6
            # There exists a consecutive pair of identical digits
            and any(digits[i - 1] == digits[i] for i in range(1, 6))
            # Digits are non-decreasing when reading left-to-right
            and all(digits[i - 1] <= digits[i] for i in range(1, 6)))


def fits_super_criteria(number: int) -> bool:
    digits = str(number)
    return (fits_criteria(number)
            # One digit must appear twice but not trice consecutively
            and any(f'{d}{d}' in digits and f'{d}{d}{d}' not in digits
                    for d in range(10)))


def solve_part_one():
    valid_numbers = [
        number for number in range(lower, upper + 1)
        if fits_criteria(number)
    ]
    print("Part one:", len(valid_numbers), valid_numbers)


def solve_part_two():
    valid_numbers = [
        number for number in range(lower, upper + 1)
        if fits_super_criteria(number)
    ]
    print("Part two:", len(valid_numbers), valid_numbers)


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
