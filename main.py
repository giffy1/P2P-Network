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
from util import generate_random_coordinate
from params import grid_size, pillar_locations, damage_by_landing, damage_other, pig_locations, bird_landing, bird_time_of_flight, n_pigs

p2p.exit_flag = 0 # set to 1 to indicate that P2P communication threads should terminate

grid = np.zeros(grid_size)
for pillar_loc in pillar_locations:
    grid[pillar_loc] = -1
    
def get_pig_by_location(pigs, location):
    for pig in pigs:
        if pig.location == location:
            return pig
            
def get_neighbors(location):
    neighbors = []
    if location[0] > 0:
        neighbors.append((location[0]-1, location[1]))
    if location[1] > 0:
        neighbors.append((location[0], location[1]-1))
    if location[0] < grid_size[0]-1:
        neighbors.append((location[0]+1, location[1]))
    if location[1] < grid_size[1]-1:
        neighbors.append((location[0], location[1]+1))
    return neighbors
    
def get_open_neighbors(location):
    open_neighbors = []
    neighbors = get_neighbors(location)
    for neighbor in neighbors:
        if grid[neighbor] == 0:
            open_neighbors.append(neighbor)
    return open_neighbors


pigs = []
# TODO : if the first pig is the one hit, then currently, it won't respond properly
location = (-1,-1) # initial coordinates outside of the grid to ensure we enter the generation loop
for i in range(n_pigs):
    pigID = 9001+i
    while location == (-1,-1) or grid[location] != 0:
        location = generate_random_coordinate(grid_size)
    location = pig_locations[i]
    grid[location] = i+1
    pigs.append(Pig(('localhost', pigID), location, 0))

# construct circular P2P network
prev_pig = pigs[0]
for pig in pigs[1:]:
    pig.set_open_neighbors(get_open_neighbors(pig.location))
    prev_pig.connect(pig)
    prev_pig = pig
prev_pig.connect(pigs[0])

print "Bird landing at location {}".format(bird_landing)
print "Starting locations:"
print grid

pigs[0].broadcast_bird_approaching(bird_landing, 3)

time.sleep(bird_time_of_flight)

if (get_pig_by_location(pigs, bird_landing)):
    get_pig_by_location(pigs, bird_landing).set_open_neighbors([])
# refresh grid and decrement status of each pig if hit
grid = np.zeros(grid_size)
for pillar_loc in pillar_locations:
    grid[pillar_loc] = -1
    
for pig in pigs:
    grid[pig.location] = pig.get_id()

hit_grid = np.zeros_like(grid) # indicates which spaces were hit, so that recursive 
# nature of pigs knocking over pillars doesn't recurse to alreay hit locations

def propagate_hit(location):
    for neighbor in get_neighbors(location):
        if hit_grid[neighbor] == 1:
            continue
        elif grid[neighbor] > 0:
            get_pig_by_location(pigs, neighbor).status -= damage_other
            hit_grid[neighbor]=1
        elif grid[neighbor] < 0:
            hit_grid[neighbor]=1
            propagate_hit(neighbor)

if grid[bird_landing] > 0:
    hit_grid[bird_landing] = 1
    get_pig_by_location(pigs, bird_landing).status -= damage_by_landing
    propagate_hit(bird_landing)
    
pigs[2].request_status(4)
pigs[0].request_status_all()

# wait until requests finish
time.sleep(5)
    
print grid

p2p.exit_flag = 1