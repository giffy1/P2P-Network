# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:39:29 2017

@author: snoran
"""

import numpy as np

def manhattan_distance(location1, location2):
    """
    Returns the Manhattan distance between two locations.
    """
    return np.sum(np.abs(np.subtract(location1, location2)))
    
def generate_random_coordinate(grid_size):
    """
    Generates a random coordinate in a 2D grid with the given dimensions.
    """
    return (np.random.randint(0,grid_size[0]), np.random.randint(0,grid_size[1]))