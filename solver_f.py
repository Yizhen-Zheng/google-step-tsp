from common import read_input, format_tour
from util import construct_dist_matrix_zero, split_cities, connect_sub_tour, calculate_total_distance, distance
from city_manager import CityManager
import sys


def solve(cities, dist_matrix=[]):
    '''
    use city-spliter with 2-opt solution
    args: cities: the formattted coordinate of each vertex
    return: tour: the order(indexes of coordinates in cities list) of visit
    first visit cities using greedy
    then resolve all crosses using 2 opt swap
    '''
    N = len(cities)
    if len(dist_matrix) == 0:
        dist_matrix = construct_dist_matrix_zero(cities)
    # a N*N matrix represent distance between every 2 cities, where N is total city number
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]
    # find initial tour through greedy
    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist_matrix[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    # 2-opt-swap
    tour = iterative_improve(tour, dist_matrix)
    return tour


# -------------functions used to find cross and resolve them iteratively-------------

def should_swap(a1, a2, b1, b2, dist_matrix) -> bool:
    '''
    detect if given edge forms cross 
    args: 
        a1, a2: vertex idx of edge a; b1, b2: vertex idx of edge b
    return
        if should swap, return true
    check if total distance after swapping((a1,b1), (a2,b2)) is smaller
    if is smaller, means the current should be swapped
    '''
    len_delta = - dist_matrix[a1][a2] - dist_matrix[b1][b2] + dist_matrix[a1][b1] + dist_matrix[a2][b2]
    return len_delta < 0


def two_opt_swap(i, j, tour):
    '''
    perform 2-opt swap
    args: edge a's start, edge b's start, origin tour
    returns: swapped tour
    in order to keep the path valid, any root between the cross(i+1(included) to j+1(excluded)) should be reversed
    '''
    tour[i+1:j+1] = list(reversed(tour[i+1:j+1]))
    return tour


def find_single_pair_to_swap(dist_matrix, tour) -> tuple[int]:
    '''
    loop through all combinations of edges and check if they should be swapped
    args: 
        cities: the formattted coordinate of each vertex
        tour: the order(indexes of coordinates in cities list) of visit
    return: cross: (edge_a_start, edge_a_start)
    return the first cross found
    '''

    # n-1: number of edges
    n = len(tour)

    # total edges to check: combination len(cities)*(len(cities)-1)/2
    # i, j: the idx in tours(the order to visit), not the idx in cities
    for i in range(n):
        # skip current edge and next edge
        for j in range(i+2, n):

            # skip last edge that back to origin(other wise it will be detected as a cross)
            if j == n-1 and i == 0:
                continue
            edge_a_start = tour[i]
            edge_a_end = tour[i+1]
            edge_b_start = tour[j]
            edge_b_end = tour[(j+1) % n]  # the last edge's vertex will be (tour[-1], tour[1])
            if should_swap(edge_a_start, edge_a_end, edge_b_start, edge_b_end, dist_matrix):
                return (i, j)
                # add the idx of start vertex of edge a and start vertex of edge b in order to swap

    return (-1, -1)


def iterative_improve(tour, dist_matrix):
    '''
    find single cross and resolve it, until no cross remind
    '''
    current_distance = calculate_total_distance(tour, dist_matrix)
    MAXIMUM_ITERATION = 10000
    i = 0
    while i < MAXIMUM_ITERATION:
        i, j = find_single_pair_to_swap(dist_matrix, tour)
        if i == -1 and j == -1:
            # if there's no remainning cross to swap
            break
        tour = two_opt_swap(i, j, tour)
        current_distance = calculate_total_distance(tour, dist_matrix)
        print(current_distance)
        i += 1
    return tour


def driver_code(data_idx):
    '''
    use city_manager to solve subcities and merge them
    '''
    cities = read_input(f'input_{data_idx}.csv')
    city_manager = CityManager('f', data_idx)
    # create dist_matrix for all cities, which is not used in solver, so save to disk and remove from memory
    city_manager.create_and_save_global_distance_matrix(cities, construct_dist_matrix_zero)
    # split subcity with their original idx and coordinates, then save to disk since they won't be used simultaneously
    city_manager.split_and_save_subcities(cities, split_cities)
    for subcity_idx in range(len(city_manager.subcity_files_path)):
        # only read one subcity into memory each time
        local_cities = city_manager.read_single_subcity(subcity_idx)
        local_solution = solve(local_cities)
        # write solution so disk and remove from memory
        city_manager.write_single_subcity_solution(subcity_idx, local_solution)
    # read all local solutions with local index, and convert to global index
    tour_array = city_manager.convert_to_global_tour()
    global_dist_matrix = city_manager.read_global_dist_matrix()
    # connect local solutions with greedy
    merged_tour = connect_sub_tour(global_dist_matrix, tour_array)
    print(calculate_total_distance(merged_tour, global_dist_matrix))
    # refine merged tour with 2-opt
    refined_tour = solve(cities, global_dist_matrix)
    print(calculate_total_distance(refined_tour, global_dist_matrix))

    return merged_tour


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    print(f'solver_d_split begins')
    if len(sys.argv) > 1:
        data_idx = int(sys.argv[1])
        print(f'solving with input {data_idx}')
        tour = driver_code(data_idx)
        formatted_tour = format_tour(tour)
        with open(f'output_f/output_{data_idx}.csv', 'w') as f:
            f.write(formatted_tour + '\n')
