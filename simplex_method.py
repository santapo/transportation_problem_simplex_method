#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 18:05:17 2020

@author: santapo
"""

from initial_feasible_solution import north_west_corner
from balancing import get_balenced_tp
import numpy as np


# get u and v
def get_us_and_vs(bfs, costs):
    us = [None] * len(costs)
    vs = [None] * len(costs[0])
    us[0] = 0
    bfs_copy = bfs.copy()
    while len(bfs_copy) > 0:
        for index, bv in enumerate(bfs_copy):
            i, j = bv[0]
            if us[i] is None and vs[j] is None: continue
            
            cost = costs[i][j]
            if us[i] is None:
                us[i] = cost - vs[j]
            else:
                vs[j] = cost - us[i]
            bfs_copy.pop(index)
            break
        
    return us, vs

# calculate delta
def get_delta(bfs, costs, us, vs):
    delta = []
    for i, row in enumerate(costs):
        for j, cost in enumerate(row):
            non_basic = all([p[0] != i or p[1] != j for p, v in bfs])
            if non_basic:
                delta.append((i,j), us[i] + vs[j] - costs)
                
    return delta

# check optimal solution
def can_be_improved(delta):
    for p, v in delta:
        if v > 0: return True
    return False


# find the largest value of delta
def get_entering_variable_position(delta):
    delta_copy = delta.copy()
    delta_copy.sort(key=lambda w: w[1])
    return delta_copy[-1][0]

# find aceptable circle in transportation problem
# return the circle and new basic variables
def get_possible_next_nodes(loop, not_visited):
    last_node = loop[-1]
    nodes_in_row = [n for n in not_visited if n[0] == last_node[0]]
    nodes_in_column = [n for n in not_visited if n[1] == last_node[1]]
    if len(loop) < 2:
        return nodes_in_row + nodes_in_column
    else:
        prev_node = loop[-2]
        row_move = prev_node[0] == last_node[0]
        if row_move: return nodes_in_column
        return nodes_in_row

def get_loop(bv_positions, ev_positions):
    def inner(loop):
        if len(loop) > 3:
            can_be_closed = len(get_possible_next_nodes(loop, [ev_positions])) == 1
            if can_be_closed: return loop
            
        not_visited = list(set(bv_positions) - set(loop))
        possible_next_nodes = get_possible_next_nodes(loop, not_visited)
        for next_node in possible_next_nodes:
            new_loop = inner(loop + [next_node])
            if new_loop: return new_loop
    
    return inner([ev_positions])

def loop_pivoting(bfs, loop):
    even_cells = loop[0::2]
    odd_cells = loop[1::2]
    get_bv = lambda pos: next(v for p, v in bfs if p == pos)
    leaving_position = sorted(odd_cells, key=get_bv)[0]
    leaving_value = get_bv(leaving_position)
    
    new_bfs = []
    for p, v in [bv for bv in bfs if bv[0] != leaving_position] + [(loop[0], 0)]:
        if p in even_cells:
            v += leaving_value
        elif p in odd_cells:
            v -= leaving_value
        new_bfs.append((p, v))
        
    return new_bfs


# final algorithm
def transportation_simplex_method(supply, demand, costs, penalties = None):
    balanced_supply, balanced_demand, balanced_costs = get_balenced_tp(supply, demand, costs)
    def inner(bfs):
        us, vs = get_us_and_vs(bfs, balanced_costs)
        delta = get_delta(bfs, balanced_costs, us, vs)
        if can_be_improved(delta):
            ev_position = get_entering_variable_position(delta)
            loop = get_loop([p for p, v in bfs], ev_position)
            return inner(loop_pivoting(bfs, loop))
        return bfs
    basic_variables = inner(north_west_corner(balanced_supply, balanced_demand))
    solution = np.zeros((len(costs), len(costs[0])))
    for (i,j), v in basic_variables:
        solution[i][j] = v
    return solution






