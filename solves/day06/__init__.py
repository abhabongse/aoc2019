"""
Day 6: Universal Orbit Map
"""
import math
import os
from collections import defaultdict, deque

import numpy as np
from tqdm import trange

this_dir = os.path.dirname(os.path.abspath(__file__))
orbits_sample_file = os.path.join(this_dir, "sample.txt")
orbits_file = os.path.join(this_dir, "orbits.txt")


def read_orbits(file):
    with open(file) as fobj:
        return [tuple(line.strip().split(")"))
                for line in fobj]


################
# For part one #
################

def orbits_to_transitive_mat(orbit_pairs):
    bodies = sorted({
        body
        for orbit_pair in orbit_pairs
        for body in orbit_pair
    })
    bodies = {body: index for index, body in enumerate(bodies)}
    mat = np.identity(len(bodies), dtype='int8')
    for center, surround in orbit_pairs:
        mat[bodies[center], bodies[surround]] = 1
    return mat


def mul_bool(fst, snd):
    return np.where(fst @ snd, 1, 0).astype('int8')


def transitive_closure(mat):
    res = mat
    times = int(math.log2(mat.shape[0])) + 1
    for _ in trange(times + 2):
        res = mul_bool(res, res)
    return res


def solve_part_one():
    # orbit_pairs = [('A', 'B'), ('B', 'C')]
    # orbit_pairs = read_orbits(orbits_sample_file)
    orbit_pairs = read_orbits(orbits_file)
    mat = orbits_to_transitive_mat(orbit_pairs)
    mat = transitive_closure(mat)
    result = np.sum(mat) - mat.shape[0]
    print(result)


################
# For part two #
################

def orbits_to_adjacency_list(orbit_pairs):
    adjlist = defaultdict(list)
    for fst, snd in orbit_pairs:
        adjlist[fst].append(snd)
        adjlist[snd].append(fst)
    return adjlist


def bfs(adjlist, src, dest):
    queue = deque([(src, 0)])
    distances = {}
    while queue:
        curr, dist = queue.popleft()
        if curr in distances:
            continue
        distances[curr] = dist
        for next in adjlist[curr]:
            queue.append((next, dist + 1))
    return distances[dest]


def solve_part_two():
    orbit_pairs = read_orbits(orbits_file)
    adjlist = orbits_to_adjacency_list(orbit_pairs)
    result = bfs(adjlist, 'YOU', 'SAN') - 2
    print(result)


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
