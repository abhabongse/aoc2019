"""
Day 4: Secure Container
"""


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


def p1_number_on_criteria(lower: int, upper: int):
    valid_numbers = [
        number for number in range(lower, upper + 1)
        if fits_criteria(number)
    ]
    count = len(valid_numbers)
    print(f"Part one: {count=}")


def p2_number_on_super_criteria(lower: int, upper: int):
    valid_numbers = [
        number for number in range(lower, upper + 1)
        if fits_super_criteria(number)
    ]
    count = len(valid_numbers)
    print(f"Part two: {count=}")


if __name__ == '__main__':
    lower = 271973
    upper = 785961

    p1_number_on_criteria(lower, upper)
    p2_number_on_super_criteria(lower, upper)
