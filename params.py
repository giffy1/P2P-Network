# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 19:59:47 2017

@author: snoran
"""

grid_size = (4,4)
pillar_locations = [(1,0), (3,3)]

delay = 0

n_pigs = 6
pig_locations=[(0,0), (0,3), (1,3), (2,2), (2,3), (3,2)]
#pig_locations=[(0,0), (0,3), (1,3), (1,2), (2,3), (3,2)]

# indicates the amount of damage a pig suffers if hit by the bird's landing:
damage_by_landing = 2
# indicates the amount of damage a pig suffers if adjacent to a fallen pig or a fallen pillar
damage_other = 1

bird_landing = (2,3) # generate_random_coordinate(grid_size)
bird_time_of_flight = 3 # number of seconds the bird requires to land