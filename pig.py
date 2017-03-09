# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 20:36:38 2017

@author: snoran
"""

from p2p import P2PNode
import numpy as np

class Pig(P2PNode):
    def __init__(self, address, location):
        P2PNode.__init__(self, address)
        self.location = location
        self.status = 10 # the status is an integer indicating how many times it can be hit
        
    def get_id(self):
        """
        Returns a readable unique pig identifier. Pigs can be identified by IP and port, 
        but incremental identifiers are more readable. So we assume a 1-to-1 mapping 
        from port (because the IP is always localhost, we can ignore it) to ID.
        """
        
        return self.address[1]-9000
        
    def broadcast_bird_approaching(self, location, hop_count=-1):
        self.send_message({'sender' : self.get_id(), 'action' : 'bird_approaching', 'propagate' : True, 'location' : location, 'hop_count' : hop_count})
        
    def take_shelter(self, location, hop_count=10):
        """
        Note: Although the method signature given in the assignment is take_shelter(pigID), 
        where I believe the pigID refers to the neighbor pig, I chose to design it such that 
        is informing its neighbors can simply send its position over the P2P network, since 
        pigs can easily check whether they are neighbors by comparing the positions.
        """
        self.send_message({'sender' : self.get_id(), 'action' : 'take_shelter', 'propagate': True, 'location' : location, 'hop_count': hop_count})
        
        return
        
    def _propagate_message(self, message):
        """
        Propogates the given message through the peer-to-peer network, decrementing the hop count.
        """
        message['hop_count'] -= 1 # decrement hop count
        if message['hop_count'] > 0 and message['sender'] != self.get_id():
            self.send_message(message)
        elif message['sender'] == self.get_id():
            print "Pig{} was the initial sender of message with action {}; there's no need to propagate the message any further.".format(self.get_id(), message['action'])
        else:
            print "Pig{} could not send message; no hops left!".format(self.get_id())
        
    def _manhattan_distance(self, location1, location2):
        """
        Returns the Manhattan distance between two locations.
        """
        return np.sum(np.abs(np.subtract(location1, location2)))
        
    def on_message_received(self, message):
        print "Pig{} received message with action {}.".format(self.get_id(), message['action'])
        if message['action'] == 'bird_approaching':
            landing_location = tuple(message['location'])
            if landing_location == self.location:
                print "Pig{} will be hit. Notifying neighbors...".format(self.get_id())
                self.take_shelter(landing_location)
            else:
                print "Pig{} is safe.".format(self.get_id())
        elif message['action'] == 'take_shelter':
            if self._manhattan_distance(message['location'], self.location) == 1:
                print "Pig{} must move".format(self.get_id())
                self.location = (self.location[0]+1, self.location[1]) # TODO: Move more intelligently than this
            else:
                print "However, pig{} is not in danger".format(self.get_id())
#        print "Pig{} received message from pig{} with content: {}".format(self.get_id(), message['sender'], message['content'])
#        print "location:", message['location']
#        print "hop count:", message['hop_count']
        if message['propagate']:
            self._propagate_message(message)
                
    def status(self):
        """
        Returns the status of the pig.
        """
        return self.status