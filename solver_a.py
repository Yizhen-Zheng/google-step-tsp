from common import read_input, write_all_output, write_single_output, INPUT_FILE_NAME, capy_res_to_visualize
from util import distance, construct_dist_matrix
import sys


def solve(cities):
    '''

    '''
    print(cities)

    N = len(cities)
    dist = construct_dist_matrix(cities)
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour


def find_cross():
    return


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    print('solver_a begins')
    if len(sys.argv) > 1:
        data_idx = int(sys.argv[1])
        print(f'solving with input {data_idx}')
        cities = read_input(INPUT_FILE_NAME[data_idx])
        tour = solve(cities)
        print(tour)
        # write_single_output(solve, 'a', 0)
    else:
        print('')
        capy_res_to_visualize('a')
        # write_all_output(solve, 'a')

    print('solver_a finished')
