from common import read_input, format_tour
from util import construct_dist_matrix_inf, split_cities, connect_sub_tour
from city_manager import CityManager
import sys


def solve(cities):
    '''
    idea: get lower bound from matrix reduction, and upper bound is infinity
    row: start, col: end. e.g., dist_matrix[1][2] means cost from city 1 to city 2
    use city spliter with branch bound
    try to avoid making deepcopy for memory efficient
    '''
    # a N*N matrix represent distance between every 2 cities, where N is total city number

    dist_matrix = construct_dist_matrix_inf(cities)
    # prepare the reduced matrix and lower bound
    reduced_dist_matrix, low_bound = reduce_matrix(dist_matrix)

    tour, cost = backtrace_explore_recursive_driver(low_bound, reduced_dist_matrix)
    print(cost)
    return tour


def backtrace_explore_recursive_driver(low_bound, dist_matrix):
    '''
    make a outer scope for backtrace_explore_recursive to store global shared variables
    '''
    best_tour = []
    best_cost = float('inf')
    N = len(dist_matrix)

    def backtrace_explore_recursive(current_city, current_bound, tour_so_far, dist_matrix):
        '''
        seems explore in greedy order has a trade-off that we need to store all origin values to backtrace 
        '''
        nonlocal best_cost, best_tour

        if len(tour_so_far) == len(dist_matrix):
            # means we've completed a tour, add back to start cost
            total_cost = current_bound+dist_matrix[current_city][0]
            if total_cost < best_cost:
                best_cost = tour_so_far

        original_row = dist_matrix[current_city][:]

        for next_city in range(N):
            if dist_matrix[next_city][current_city] != float('inf'):
                # add cost before eliminating
                current_to_next_cost = dist_matrix[current_city][next_city]
                # add backtrace before eliminating
                original_col = [dist_matrix[i][next_city] for i in range(N)]
                original_back_edge = dist_matrix[next_city][current_city]
                # eliminate current city's row, next city's col, next city to current city
                for i in range(N):
                    dist_matrix[current_city][i] = float('inf')
                    dist_matrix[i][next_city] = float('inf')
                dist_matrix[next_city][current_city] = float('inf')
                # reduce
                _, reducted_cost = reduce_matrix(dist_matrix)
                new_bound = current_bound+current_to_next_cost+reducted_cost

                if new_bound < best_cost:
                    # explore if new_bound smaller than current upper bound
                    tour_so_far.append(next_city)
                    backtrace_explore_recursive(next_city, new_bound, tour_so_far, dist_matrix)
                    tour_so_far.pop()
                # restore the dist matrix
                for i in range(N):
                    dist_matrix[current_city][i] = original_row[i]
                    dist_matrix[i][next_city] = original_col[i]
                dist_matrix[next_city][current_city] = original_back_edge

    backtrace_explore_recursive(0, low_bound, [0], dist_matrix)
    return best_tour, best_cost


def reduce_matrix(dist_matrix):
    '''
    reduce matrix and find potentail smallest cost(the low bound)
    by doing this, each row and col in reduced matrix will have as least one 0
    args: dist_matrix
    return:
        inplace modified dist_matrix
        reduced dist matrix
        total reduced cost(low bound)
    '''

    N = len(dist_matrix)
    low_bound = 0
    for row in range(N):
        mininal_dist_in_row = min(dist_matrix[row])
        if mininal_dist_in_row != float('inf'):
            # skip when the whole rol is already eliminated
            for i in range(N):
                dist_matrix[row][i] = dist_matrix[row][i] - \
                    mininal_dist_in_row if dist_matrix[row][i] != float('inf') else dist_matrix[row][i]
            low_bound += mininal_dist_in_row
    for col in range(N):
        mininal_dist_in_col = min([dist_matrix[i][col] for i in range(N)])
        if mininal_dist_in_col != float('inf'):
            # skip when the whole col is already eliminated
            for i in range(N):
                dist_matrix[i][col] = dist_matrix[i][col] - \
                    mininal_dist_in_col if dist_matrix[i][col] != float('inf') else dist_matrix[i][col]
            low_bound += mininal_dist_in_col

    return dist_matrix, low_bound


def driver_code(data_idx):
    '''
    use city_manager to solve subcities and merge them
    '''
    cities = read_input(f'input_{data_idx}.csv')
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
