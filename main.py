# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:55:32 2017

Sean Noran
Distributed Operating Systems
Lab 1 P2P Network

This is an implementation of a P2P Network, where nodes are represented 
by pigs in a grid. Angry birds are tossed at the grid and pigs must 
communicate the predicted landing coordinates of the birds in order to 
save their fellow pigs. This is done in a peer-to-peer network, where 
pigs can broadcast a bird's landing location (within a certain number of 
peer-to-peer hops) and each pig can inform physical neighbors to take 
shelter.

"""

import time
import numpy as np
from pig import Pig
import p2p
from util import manhattan_distance

p2p.exit_flag = 0 # set to 1 to indicate that P2P communication threads should terminate

grid_size = (2,2) # we'll work with a 5 x 5 grid to start
grid = np.zeros(grid_size)

def generate_random_coordinate(grid_size):
    """
    Generates a random coordinate in a 2D grid with the given dimensions.
    """
    return (np.random.randint(0,grid_size[0]), np.random.randint(0,grid_size[1]))

# indicates the amount of damage a pig suffers if hit by the bird's landing:
damage_by_landing = 2
# indicates the amount of damage a pig suffers if adjacent to a pig affected by the landing:
damage_by_adjacent_pig = 1

bird_landing = generate_random_coordinate(grid_size)
bird_time_of_flight = 3 # number of seconds the bird requires to land

n_pigs = 3
pigs = []
# TODO : if the first pig is the one hit, then currently, it won't respond properly
location = (-1,-1) # initial coordinates outside of the grid to ensure we enter the generation loop
for i in range(n_pigs):
    pigID = 9001+i
    while location == (-1,-1) or grid[location]:
        location = generate_random_coordinate(grid_size)
    grid[location] = i+1
    pigs.append(Pig(('localhost', pigID), location))

# construct circular P2P network
prev_pig = pigs[0]
for pig in pigs[1:]:
    prev_pig.connect(pig)
    prev_pig = pig
prev_pig.connect(pigs[0])

pigs[0].broadcast_bird_approaching(bird_landing, 3)

time.sleep(bird_time_of_flight)

# refresh grid and decrement status of each pig if hit
grid = np.zeros(grid_size)
for pig in pigs:
    grid[pig.location] = pig.get_id()
    if pig.location == bird_landing:
        pig.status -= damage_by_landing
    if manhattan_distance(pig.location, bird_landing):
        pig.status -= damage_by_adjacent_pig
    
pigs[2].request_status(20)
#for pig in pigs:
#    print pig.get_id(), pig.status

time.sleep(3)

pigs[0].request_status_all()

time.sleep(3)
p2p.exit_flag = 1
    
print grid
#node1 = P2PNode(('localhost', 9999))
#node2 = P2PNode(('localhost', 8888))
#
#node1.connect(node2)