from common import driver_code
from util import distance, construct_dist_matrix_smarter, calculate_total_distance
import sys
from copy import deepcopy


def solve(cities):
    '''
    idea: get lower bound from matrix reduction, and upper bound is infinity
    row: start, col: end. e.g., dist_matrix[1][2] means cost from city 1 to city 2
    '''
    N = len(cities)
    # a N*N matrix represent distance between every 2 cities, where N is total city number
    dist_matrix = construct_dist_matrix_smarter(cities)
    # prepare the reduced matrix and lower bound
    reduced_dist_matrix, low_bound = reduce_matrix(dist_matrix)

    tour, cost=explore(reduced_dist_matrix,low_bound)

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
    new_dist_matrix=deepcopy(origin_dist_matrix)
    N = len(new_dist_matrix)
    low_bound = 0
    for row in range(N):
        mininal_dist_in_row = min(new_dist_matrix[row])
        new_dist_matrix[row] = list(map(lambda d: d-mininal_dist_in_row, new_dist_matrix[row]))
        low_bound += mininal_dist_in_row
    for col in range(N):
        mininal_dist_in_col = min([new_dist_matrix[i][col] for i in range(N)])
        for i in range(N):
            new_dist_matrix[i][col] -= mininal_dist_in_col
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
    N=len(new_matrix)
    new_matrix=deepcopy(origin_matrix)
    new_matrix[start]=[float('inf')]*N   # mark row of start as inf
    for i in range(N):  # mark column of end as inf
        new_matrix[i][end]=float('inf')
    new_matrix[end][start]=float('inf')
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
    N=len(initial_reduced_matrix)
    stack=[(0,low_bound,[0],initial_reduced_matrix)]  # start from city 0  
    best_tour=[]
    upper_bound=float('inf') #global shared upper_bound, initialize as inf(any finished path will update it)
    while stack:
        current_city, current_low_bound, tour_so_far, current_dist_matrix=stack.pop()
        # current_city is proofed to be pruned 
        for next_city in range(0,N,-1): 
            #keep first to check final city, reverse to achieve recursion order
            if current_dist_matrix[current_city][next_city]!=float('inf'):
                # check if explore before pushing to staxk to reduce the stack size (called early pruning)
                new_eliminated_matrix=eliminate_visited(current_dist_matrix,current_city,next_city)
                new_reduced_matrix,new_cost=reduce_matrix(new_eliminated_matrix)
                new_low_lound=current_low_bound+new_cost #add cost to go next city
                if new_low_lound<upper_bound:
                    # compare, if explore next_city cost less than known best cost
                    if next_city==0:
                        # if we find better way to finish the tour:
                        # no need to push first city to tour again
                        # update best_tour and best cost(upper_bound)
                        best_tour=tour_so_far
                        upper_bound=new_low_lound
                    else:
                        # haven't finished, explore next city
                        new_tour_so_far=tour_so_far.append(next_city)
                        stack.append((next_city,new_low_lound,new_tour_so_far,new_reduced_matrix))

    return best_tour, upper_bound

if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    driver_code('d', solve)
