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

p2p.exit_flag = 0    
        
bird_landing = (2,3)
pigs = []
# TODO : if the first pig is the one hit, then currently, it won't respond properly
pig1 = Pig(('localhost', 9001), (3,3))
pig2 = Pig(('localhost', 9002), (2,3))
pig3 = Pig(('localhost', 9003), (0,1))
pigs.append(pig1)
pigs.append(pig2)
pigs.append(pig3)

pig1.connect(pig2)
pig2.connect(pig3)
pig3.connect(pig1)

#prev_pig = pigs[0]
#for pig in pigs[1:]:
#    prev_pig.connect(pig)
#    #pig.connect(prev_pig)
#pig.connect(pigs[0])

#pig1.connect(pig2)
#pig2.connect(pig3)
pig1.broadcast_bird_approaching(bird_landing, 3)

time.sleep(3)

# we'll work with a 5 x 5 grid to start
grid = np.zeros((5,5))

for pig in pigs:
    grid[pig.location] = pig.get_id()
    if pig.location == bird_landing:
        pig.status -= 1
    
pig3.request_status(20)
#for pig in pigs:
#    print pig.get_id(), pig.status

time.sleep(3)
p2p.exit_flag = 1
    
print grid
#node1 = P2PNode(('localhost', 9999))
#node2 = P2PNode(('localhost', 8888))
#
#node1.connect(node2)