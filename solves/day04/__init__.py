"""
Day 4: Secure Container
"""

lower = 271973
upper = 785961


def fits_criteria(number):
    digits = str(number)
    if len(digits) != 6:
        return False
    if not any(digits[i - 1] == digits[i] for i in range(1, 6)):
        return False
    if not all(digits[i - 1] <= digits[i] for i in range(1, 6)):
        return False
    return True


def fits_super_criteria(number):
    if not fits_criteria(number):
        return False
    digits = str(number)
    for test in range(10):
        double = f'{test}{test}'
        triple = f'{test}{test}{test}'
        if double in digits and triple not in digits:
            return True
    return False


def solve_part_one():
    valid_numbers = [number for number in range(lower, upper + 1)
                     if fits_criteria(number)]
    print(len(valid_numbers), valid_numbers)


def solve_part_two():
    valid_numbers = [number for number in range(lower, upper + 1)
                     if fits_super_criteria(number)]
    print(len(valid_numbers), valid_numbers)



if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
