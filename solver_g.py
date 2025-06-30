from common import read_input, format_tour
from util import construct_dist_matrix_inf_pheromone, split_cities, connect_sub_tour, calculate_total_distance
from city_manager import CityManager
import sys


VAPORIZATION_RATE = 0.001


def solve(cities):
    '''
    ant colony optimization
    pheromone budget for each ant: 1/path_len
    '''
    # a N*N matrix represent distance between every 2 cities, where N is total city number
    dist_matrix, pher_matrix = construct_dist_matrix_inf_pheromone(cities)

    tour = []

    return tour


def choose_next_city(current_city):
    '''
    choose next city to move based on pheromone
    '''
    return


def update_pheromone():
    '''
    '''
    return


def calculate_delta(tours, dist_matrix, pher_matrix):
    '''
    after n ants finished travel, calculate t 
    '''
    path_len = calculate_total_distance(tour, dist_matrix)
    delta_of_k = 1/path_len


def iterative_explore(cities, dist_matrix, pher_matrix):
    '''
    the main loop to explore and update pheromone matrix
    '''
    N = len(cities)
    VAPORIZATION_RATE = 0.001
    # conditional decide ant group size
    if N < 64:
        ANT_GROUP_SIZE = N
        MAX_ITER = 1000
    elif 64 <= N < 128:
        ANT_GROUP_SIZE = 1.2*N
        MAX_ITER = 3000
    elif 128 < N <= 512:
        ANT_GROUP_SIZE = 0.8*N
        MAX_ITER = 5000
    else:
        ANT_GROUP_SIZE = 0.5*N
        MAX_ITER = 10000


def driver_code(data_idx):
    '''
    use city_manager to solve subcities and merge them
    '''
    cities = read_input(f'input_{data_idx}.csv')
    if len(cities) > 500:
        city_manager = CityManager('e', data_idx)
        city_manager.create_and_save_global_distance_matrix(cities, construct_dist_matrix_inf)
        city_manager.split_and_save_subcities(cities, split_cities)
        for subcity_idx in range(len(city_manager.subcity_files_path)):
            local_cities = city_manager.read_single_subcity(subcity_idx)
            local_solution = solve(local_cities)
            city_manager.write_single_subcity_solution(subcity_idx, local_solution)
        tour_array = city_manager.convert_to_global_tour()
        global_dist_matrix = city_manager.read_global_dist_matrix()
        merged_tour = connect_sub_tour(global_dist_matrix, tour_array)
        return merged_tour
    else:
        tour = solve(cities)
        return tour


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''

    print(f'solver_d_split begins')
    if len(sys.argv) > 1:
        data_idx = int(sys.argv[1])
        print(f'solving with input {data_idx}')
        tour = driver_code(data_idx)
        formatted_tour = format_tour(tour)
        with open(f'output_d_split/output_{data_idx}.csv', 'w') as f:
            f.write(formatted_tour + '\n')
