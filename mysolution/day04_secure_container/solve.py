from __future__ import annotations

import more_itertools


def main():
    lower = 271973
    upper = 785961

    # Part 1
    p1_answer = sum(
        digits_are_non_decreasing(n) and exists_adjacent_identical_pair(n)
        for n in range(lower, upper + 1)
    )
    print(p1_answer)

    # Part 2
    p2_answer = sum(
        digits_are_non_decreasing(n) and exists_adjacent_identical_pair_not_triplet(n)
        for n in range(lower, upper + 1)
    )
    print(p2_answer)


def digits_are_non_decreasing(number: int) -> bool:
    return all(x <= y for x, y in more_itertools.windowed(str(number), n=2))


def exists_adjacent_identical_pair(number: int) -> bool:
    number = str(number)
    return any(f'{d}{d}' in number for d in range(10))


def exists_adjacent_identical_pair_not_triplet(number: int) -> bool:
    number = str(number)
    return any(f'{d}{d}' in number and f'{d}{d}{d}' not in number for d in range(10))


if __name__ == '__main__':
    main()
