from common import read_input, format_tour
from util import construct_dist_matrix_inf, split_cities, connect_sub_tour
from copy import deepcopy
from city_manager import CityManager
import sys


def solve(cities):
    '''
    idea: get lower bound from matrix reduction, and upper bound is infinity
    row: start, col: end. e.g., dist_matrix[1][2] means cost from city 1 to city 2
    use city spliter with branch bound
    this one use deepcopy for every child, which is memory-costy
    '''
    # a N*N matrix represent distance between every 2 cities, where N is total city number
    dist_matrix = construct_dist_matrix_inf(cities)
    # prepare the reduced matrix and lower bound
    reduced_dist_matrix, low_bound = reduce_matrix(dist_matrix)
    tour, cost = explore(reduced_dist_matrix, low_bound)
    print(cost)
    return tour


def reduce_matrix(origin_dist_matrix):
    '''
    reduce matrix and find potentail smallest cost(the low bound)
    by doing this, each row and col in reduced matrix will have as least one 0
    args: origin dist_matrix
    return:
        reduced dist matrix
        total reduced cost(low bound)
    '''
    new_dist_matrix = deepcopy(origin_dist_matrix)
    N = len(new_dist_matrix)
    low_bound = 0
    for row in range(N):
        mininal_dist_in_row = min(new_dist_matrix[row])
        if mininal_dist_in_row != float('inf'):
            # skip when the whole rol is already eliminated
            for i in range(N):
                new_dist_matrix[row][i] = new_dist_matrix[row][i] - \
                    mininal_dist_in_row if new_dist_matrix[row][i] != float('inf') else new_dist_matrix[row][i]
            low_bound += mininal_dist_in_row
    for col in range(N):
        mininal_dist_in_col = min([new_dist_matrix[i][col] for i in range(N)])
        if mininal_dist_in_col != float('inf'):
            # skip when the whole col is already eliminated
            for i in range(N):
                new_dist_matrix[i][col] = new_dist_matrix[i][col] - \
                    mininal_dist_in_col if new_dist_matrix[i][col] != float('inf') else new_dist_matrix[i][col]
            low_bound += mininal_dist_in_col

    return new_dist_matrix, low_bound


def eliminate_visited(origin_matrix, start, end):
    '''
    make a copy of origin maxtrix
    note: recieve the new_dist_matrix with a new var, avoid modifying origin_matrix(which will be passed to other branches)
    args:
        origin_matrix
        start: the city start from on current edge
        end: the city end at on current edge
    return:
        a copy of original matrix that:
            mark matrix[start][i] row as inf, means we can not use start city as start twice, 
            mark matrix[i][end] column ad inf, means we can not go to the end city twice from any cities
            mark matrix[end][start] as inf, means we can not go from end back to start
    '''
    N = len(origin_matrix)
    new_matrix = deepcopy(origin_matrix)
    for i in range(N):  # mark row of start as inf
        new_matrix[start][i] = float('inf')
    for i in range(N):  # mark column of end as inf
        new_matrix[i][end] = float('inf')
    new_matrix[end][start] = float('inf')
    return new_matrix


def explore(initial_reduced_matrix, low_bound):
    '''
    args:
        initial_reduced_matrix: a deepcopy of dist_matrix, only reduced once, without marking any row/col as inf
        low_bound: initial cost after init reducing
    return:

    the main loop to explore the decision tree
    perform deepth first traverse 
    keep update the upper cound and use that upper bound to eliminate choices
    stack: (current_city, current_low_bound, current_upper_bound, tour_so_far, dist_matrix)
    update current_low_bound in each path as we explore further
    only push new city to visit if satisfy:
        current cost is not inf(visited) 
        the current_low_bound cost so far in that path is smaller than known upper bound 
    loop until cannot push to stack(all visited or eliminated)
    how to know current path finished: no more node can be pushed into stack(all marked inf)
    this means current_low_bound must be smaller than current_up_bound, so we update best tour and upper bound
    '''
    N = len(initial_reduced_matrix)
    stack = [(0, low_bound, [0], initial_reduced_matrix)]  # start from city 0
    best_tour = []
    upper_bound = float('inf')  # global shared upper_bound, initialize as inf(any finished path will update it)
    while stack:
        current_city, current_low_bound, tour_so_far, current_dist_matrix = stack.pop()
        # current_city is proofed to be pruned
        cities_to_explore = []
        for next_city in range(N):
            # check from 0 to final city
            if current_dist_matrix[current_city][next_city] != float('inf'):
                # check if explore before pushing to staxk to reduce the stack size (called early pruning)
                new_eliminated_matrix = eliminate_visited(current_dist_matrix, current_city, next_city)
                new_reduced_matrix, new_cost = reduce_matrix(new_eliminated_matrix)
                print('')
                # add cost of current to next with not eliminated matrix
                new_low_lound = current_low_bound+new_cost+current_dist_matrix[current_city][next_city]
                print(new_low_lound)  # add cost to go next city
                if new_low_lound < upper_bound:
                    # compare, if explore next_city cost less than known best cost
                    if len(tour_so_far) == N and next_city == 0:
                        # this means we've find better way to finish the tour:
                        # no need to push first city to tour again
                        # update best_tour and best cost(upper_bound)
                        best_tour = tour_so_far
                        upper_bound = new_low_lound
                    else:
                        # haven't finished, explore next city
                        new_tour_so_far = tour_so_far+[next_city]
                        cities_to_explore.append((next_city, new_low_lound, new_tour_so_far, new_reduced_matrix))
        if cities_to_explore:
            #  explore cities with lower cost first to make upper bound decrease faster
            stack.extend(sorted(cities_to_explore, key=lambda node: node[1], reverse=True))
    return best_tour, upper_bound


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
