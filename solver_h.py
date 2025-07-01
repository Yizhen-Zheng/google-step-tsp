from common import read_input, format_tour
from util import construct_dist_matrix_inf_pheromone, split_cities, connect_sub_tour, calculate_total_distance
from city_manager import CityManager
import sys
import random
import numpy as np
import solver_a as two_opt


def solve(cities):
    '''
    ant colony optimization
    pheromone budget for each ant: 1/path_len
    '''
    # a N*N matrix represent distance between every 2 cities, where N is total city number
    dist_matrix, pher_matrix = construct_dist_matrix_inf_pheromone(cities)
    tour, cost = iterative_explore(cities, dist_matrix, pher_matrix)
    print(cost)
    tour_list = convert_tour_to_list(tour)

    return tour_list


def choose_next_city(current_city, tour, dist_matrix, pher_matrix, explor_factor):
    '''
    choose next city to move based on pheromone
    first calculate probability 
    this will be called mutiple times sence it moves one step each time
    args:    
        current_city: the last city in current path to know path[-1] in O(1)
        tour: a dict contains each city and it's parent, e.g, {parent:child} 
        dist_matrix: look up matrix of distance
        pher_matrix: look up matrix of pheromone
    return:
        tour: updated tour, added the index of next city to explore
        current_city: new current city after making the move
    '''
    ALPHA = max(1, 3*explor_factor)  # influence of pheromone
    BETA = max(1, 2/explor_factor)  # influence of distance

    N = len(dist_matrix)
    total_desirability = 0
    desirabilities = []
    # calculate probability:
    for i in range(N):
        if i not in tour:
            tau = pher_matrix[current_city][i]
            eta = 1/dist_matrix[current_city][i]

            random_factor = 1+0.1*np.random.random()
            delta = pow(tau, ALPHA)*pow(eta, BETA)*random_factor
            total_desirability += delta
            desirabilities.append((i, delta))
    next_city = -1
    if total_desirability == 0:
        # edge case: to avoid devide by 0, make random choice
        next_city = np.random.choice(desirabilities)[0]
    else:
        # small change of random selection
        if np.random.random() < (1-explor_factor)*0.1:
            next_city = np.random.choice([city for city, _ in desirabilities])
        else:
            # convert to cumulative probability:
            cumulative_probability = 0
            converted_probabilities = []
            for city, desirability in desirabilities:
                prob = desirability / total_desirability
                cumulative_probability += prob
                converted_probabilities.append((city, cumulative_probability))
            # make choice by generating random float in [0,1]
            random_num = np.random.rand()
            for city, probability in converted_probabilities:
                if random_num <= probability:
                    next_city = city
                    break
    tour[current_city] = next_city
    tour[next_city] = None

    return tour, next_city


def update_pheromone(tours, pher_matrix, iter_count=0, max_iter=1000, best_tour_ever=None):
    '''
    if delta is 0, it should it should evaprizate as well
    first multiply each by rpo 
    args:
        tours: a list contains (len_of_tour,tour) 
        pher_matrix: pheromone matrix to update inplace

    '''
    base_rho = 0.05
    # rho = base_rho+0.02*(iter_count/max_iter)  # increase evaporation over time
    rho = base_rho  # increase evaporation over time

    N = len(pher_matrix)
    # perform evaporation
    for i in range(N):
        for j in range(i+1, N):  # keep diagnal 0
            pher_matrix[i][j] = pher_matrix[j][i] = (1 - rho)*pher_matrix[i][j]
    for tour_len, tour in tours:
        pher_amount = 1/tour_len
        current_city = 0
        for i in range(N):
            next_city = tour[current_city]
            if next_city == None:
                next_city = 0
            pher_matrix[current_city][next_city] += pher_amount
            pher_matrix[next_city][current_city] += pher_amount
            current_city = next_city
    if best_tour_ever is not None:
        best_len, best_tour = best_tour_ever
        elite_amount = 2.0 / best_len  # Stronger reinforcement
        current_city = 0
        for i in range(N):
            next_city = best_tour[current_city]
            if next_city is None:
                next_city = 0
            pher_matrix[current_city][next_city] += elite_amount
            pher_matrix[next_city][current_city] += elite_amount
            current_city = next_city
    return


def reset_pheromone_matrix(pher_matrix, reset_strength=0.5):
    '''
    Partially reset pheromone matrix to escape local minima
    '''
    N = len(pher_matrix)
    initial_pheromone = 1.0

    for i in range(N):
        for j in range(i+1, N):
            # Blend current pheromone with initial value
            current_value = pher_matrix[i][j]
            new_value = (1 - reset_strength) * current_value + reset_strength * initial_pheromone
            pher_matrix[i][j] = pher_matrix[j][i] = new_value


def calculate_path_len(tour, dist_matrix):
    '''
    args: 
        tour: a dict of {parent:child}
        dist_matrix: distance look up table
    if find parent:None, means it backs to start city(0) 
    return: the total length of the tour
    '''
    N = len(tour)
    total_len = 0
    current_city = 0
    for _ in range(N):
        next_city = tour[current_city]
        if next_city == None:
            total_len += dist_matrix[current_city][0]
        else:
            total_len += dist_matrix[current_city][next_city]
            current_city = next_city
    return total_len


def iterative_explore(cities, dist_matrix, pher_matrix):
    '''
    the main loop to explore and update pheromone matrix
    '''
    N = len(cities)
    # conditional decide ant group size and maximum iteration
    if N < 64:
        ANT_GROUP_SIZE = N
        MAX_ITER = 1000
    elif 64 <= N < 128:
        ANT_GROUP_SIZE = int(1.2*N)
        MAX_ITER = 3000
    elif 128 < N <= 512:
        ANT_GROUP_SIZE = int(0.8*N)
        MAX_ITER = 5000
    else:
        ANT_GROUP_SIZE = int(0.5*N)
        MAX_ITER = 10000

    iter_count = 0
    best_tour = []
    best_cost = float('inf')
    improved = False

    while iter_count < MAX_ITER:
        iter_count += 1
        tours = []
        exploration_factor = 1.0

        for _ in range(ANT_GROUP_SIZE):
            tour = {0: None}
            tour_len = 0
            current_city = 0

            while len(tour) < N:
                tour, next_city = choose_next_city(current_city, tour, dist_matrix, pher_matrix, exploration_factor)
                tour_len += dist_matrix[current_city][next_city]
                current_city = next_city
            tour_len += dist_matrix[current_city][0]
            tours.append((tour_len, tour))

        # Find best in current iteration
        iteration_best_cost = min(tour_len for tour_len, _ in tours)
        similar_tour_count = 0
        best_tour_reference = None
        # update best tour
        for tour_len, tour in tours:
            print(tour_len)
            if tour_len < best_cost:
                best_tour = tour
                best_cost = tour_len
                improved = True
            if iteration_best_cost-1 <= tour_len <= iteration_best_cost+1:
                similar_tour_count += 1
        if similar_tour_count >= int(ANT_GROUP_SIZE*0.95):
            improved = False
        print(f"Iteration: {iter_count}, Best cost so far {best_cost:.2f}")

        if not improved:
            # check if fall into local:
            print(f"Stagnation detected at iteration {iter_count}. ")
            best_tour_reference = (best_cost, best_tour)
            exploration_factor = 0.5
            reset_pheromone_matrix(pher_matrix, reset_strength=0.5)
            improved = True  # only reset once

        # update pheromone:
        update_pheromone(tours, pher_matrix, iter_count, MAX_ITER, best_tour_reference)

    return best_tour, best_cost


def convert_tour_to_list(tour):
    '''
    convert dict tour to list
    args:
        tour dict
    returns:
        tour list
    '''
    tour_list = [0]
    current_city = 0
    for _ in range(len(tour)):
        next_city = tour[current_city]
        tour_list.append(next_city)
        current_city = next_city
    return tour_list


def driver_code(data_idx):
    '''
    use city_manager to solve subcities and merge them
    '''
    cities = read_input(f'input_{data_idx}.csv')
    if len(cities) > 500:
        city_manager = CityManager('e', data_idx)
        city_manager.create_and_save_global_distance_matrix(cities, construct_dist_matrix_inf_pheromone)
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

    print(f'solver_h begins')
    if len(sys.argv) > 1:
        data_idx = int(sys.argv[1])
        print(f'solving with input {data_idx}')
        tour = driver_code(data_idx)
        formatted_tour = format_tour(tour)
        with open(f'output_h/output_{data_idx}.csv', 'w') as f:
            f.write(formatted_tour + '\n')
