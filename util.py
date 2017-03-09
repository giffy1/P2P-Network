# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:39:29 2017

@author: snoran
"""

import numpy as np

def manhattan_distance(self, location1, location2):
    """
    Returns the Manhattan distance between two locations.
    """
    return np.sum(np.abs(np.subtract(location1, location2)))