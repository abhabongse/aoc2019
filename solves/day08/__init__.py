"""
Day 8: Space Image Format
"""
import os

import numpy as np

this_dir = os.path.dirname(os.path.abspath(__file__))
image_file = os.path.join(this_dir, "image.txt")


def read_encoded_image(file):
    with open(file) as fobj:
        return fobj.read().strip()


def encoded_image_to_layers(encoded_image, width, height):
    return np.reshape([int(token) for token in encoded_image], (-1, height, width))


def solve_part_one():
    encoded_image = read_encoded_image(image_file)
    width, height = 25, 6
    image = encoded_image_to_layers(encoded_image, width, height)

    zero_digits = (image == 0).sum(axis=(1, 2))
    mzl_index = np.argmin(zero_digits)  # minimum zero layer
    mzl_layer = image[mzl_index]
    count_ones = (mzl_layer == 1).sum()
    count_twos = (mzl_layer == 2).sum()
    print(count_ones * count_twos)


def solve_part_two():
    encoded_image = read_encoded_image(image_file)
    width, height = 25, 6
    image = encoded_image_to_layers(encoded_image, width, height)

    canvas = np.ones([height, width]) * 2
    for layer in image:
        canvas = np.where(canvas < 2, canvas, layer).astype('int8')

    combined = '\n'.join(
        ''.join(row)
        for row in np.where(canvas, '#', ' ')
    )
    print(combined)


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
