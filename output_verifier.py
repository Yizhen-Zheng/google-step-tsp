#!/usr/bin/env python3


from common import read_input, distance, CHALLENGES
from util import construct_dist_matrix, calculate_total_distance

FILE_TO_VERIFY = ['outpu_a', 'outpu_b', 'outpu_c', 'sample/random', 'sample/greedy', 'sample/sa']


def verify_output():
    for challenge_number in range(CHALLENGES):
        print(f'Challenge {challenge_number}')
        cities = read_input(f'input_{challenge_number}.csv')
        dist_matrix = construct_dist_matrix(cities)

        N = len(cities)
        for output_prefix in (FILE_TO_VERIFY):
            output_file = f'{output_prefix}_{challenge_number}.csv'
            with open(output_file) as f:
                lines = f.readlines()
                assert lines[0].strip() == 'index'
                tour = [int(i.strip()) for i in lines[1:N + 1]]
            assert set(tour) == set(range(N))
            path_length = calculate_total_distance(cities, tour, dist_matrix)
            print(f'{output_prefix:16}: {path_length:>10.2f}')
        print()


if __name__ == '__main__':
    verify_output()
