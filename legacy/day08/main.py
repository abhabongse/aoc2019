"""
Day 8: Space Image Format
"""
import os

import numpy as np


def read_encoded_image(filename: str) -> str:
    with open(filename) as fobj:
        return fobj.read().strip()


def encoded_image_to_layers(encoded_image: str, width: int, height: int) -> np.ndarray:
    return np.reshape([int(token) for token in encoded_image], (-1, height, width))


def print_pixels(board: np.ndarray):
    print('\n'.join(''.join(line) for line in board))


def p1_validate(image: np.ndarray):
    zero_digits = (image == 0).sum(axis=(1, 2))
    mzl_index = np.argmin(zero_digits)  # minimum zero layer
    mzl_layer = image[mzl_index]
    count_ones = (mzl_layer == 1).sum()
    count_twos = (mzl_layer == 2).sum()
    result = count_ones * count_twos
    print(f"Part one: {result=}")


def p2_decode(image: np.ndarray):
    canvas = np.ones([height, width]) * 2
    for layer in image:
        canvas = np.where(canvas < 2, canvas, layer).astype('int8')

    print_pixels(np.where(canvas, '#', ' '))


if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    image_filename = os.path.join(this_dir, "image.txt")
    encoded_image = read_encoded_image(image_filename)

    width, height = 25, 6
    image = encoded_image_to_layers(encoded_image, width, height)

    p1_validate(image)
    p2_decode(image)
