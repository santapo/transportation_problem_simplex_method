#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 17:15:28 2020

@author: santapo
"""

def get_balenced_tp(supply,demand,costs,penalties=None):
    total_supply = sum(supply)
    total_demand = sum(demand)
    
    if total_supply < total_demand:
        if penalties is None:
            raise Exception('Supply less than demand, penlties required')
            new_supply = supply + [total_demand - total_supply]
            new_costs = costs + [penalties]
            return new_supply, demand, new_costs
    if total_supply > total_demand:
        new_demand = demand +[total_supply - total_demand]
        new_costs = costs + [[0 for _ in demand]]
        return supply, new_demand, new_costs
    return supply, demand, costs