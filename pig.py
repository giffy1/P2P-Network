# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 20:36:38 2017

@author: snoran
"""

from p2p import P2PNode

class Pig(P2PNode):
    def __init__(self, address, location, send_delay=0):
        P2PNode.__init__(self, address, send_delay)
        self.location = location
        self.status = 10 # the status is an integer indicating how many times it can be hit
        self.neighbors = [] # list of available neighboring locations
        
    def set_open_neighbors(self, neighbors):
        """
        Sets the open neighboring locations to which a pig coan move. These 
        are locations that are not occupied by another pig or by a pillar.
        """
        self.neighbors = neighbors
        
    def get_id(self):
        """
        Returns a readable unique pig identifier. Pigs can be identified by IP and port, 
        but incremental identifiers are more readable. So we assume a 1-to-1 mapping 
        from port (because the IP is always localhost, we can ignore it) to ID.
        """
        
        return self.address[1]-9000
        
    def broadcast_bird_approaching(self, location, hop_count=-1):
        """
        Notify other pigs that bird is approaching and will land at the given location. 
        The hop count indicates how many times the message can propagate through the 
        P2P network.
        """
        self.send_message({'sender' : self.get_id(), 'action' : 'bird_approaching', 'propagate' : True, 'location' : location, 'hop_count' : hop_count})
        
    def take_shelter(self, pigID, hop_count=-1):
        """
        Inform the given pig to move to another available space.
        """
        self.send_message({'sender' : self.get_id(), 'action' : 'take_shelter', 'propagate': True, 'pigID' : pigID, 'hop_count': hop_count})
        
        return
        
    def _propagate_message(self, message, direction="forward"):
        """
        Propogates the given message through the peer-to-peer network, decrementing the hop count.
        """
        message['hop_count'] -= 1 # decrement hop count
        if message['hop_count'] != 0 and message['sender'] != self.get_id():
            self.send_message(message, direction)
        elif message['sender'] == self.get_id():
            print "Pig{} was the initial sender of message with action {}; there's no need to propagate the message any further.".format(self.get_id(), message['action'])
        else:
            print "Pig{} could not send message; no hops left!".format(self.get_id())
        
    def on_message_received(self, message):
        print "Pig{} received message with action {}.".format(self.get_id(), message['action'])
        if message['action'] == 'bird_approaching':
            landing_location = tuple(message['location'])
            if landing_location == self.location:
                print "Pig{} must move. Moving to next avilable location.".format(self.get_id())
#                print "Pig{} will be hit. Notifying neighbors...".format(self.get_id())
                if len(self.neighbors) > 0:
                    self.location = self.neighbors[0] # simply choose first available location (may not be optimal but that's OK)
                else:
                    print "Could not move. There are no avilable neighboring locations..."
            else:
                print "Pig{} is safe.".format(self.get_id())
        elif message['action'] == 'take_shelter':
            if message['pigID'] == self.get_id():
                print "Pig{} taking shelter.".format(self.get_id())
                if len(self.neighbors) > 0:
                    self.location = self.neighbors[0] # simply choose first available location (may not be optimal but that's OK)
                else:
                    print "Could not move. There are no avilable neighboring locations..."
            else:
                self._propagate_message(message)
            return
        elif message['action'] == 'request_status':
            print "Pig{} received status request for pig{}.".format(self.get_id(), message['pigID'])
            if self.get_id() == message['pigID']:
                print "Pig{} responding to status request.".format(self.get_id())
                message['status'] = self.status
                message['action'] = 'respond_status'
                self._propagate_message(message, direction="backward")
            elif self.get_id() == message['sender']:
                print "Pig{} sent out a status request for pig{}. Pig{} likely doesn't exist, because the request returned to the sender.".format(self.get_id(), message['pigID'], message['pigID'])
            else:
                print "Pig{} forwarding request".format(self.get_id())
                self._propagate_message(message)
            return
        elif message['action'] == 'respond_status':
            print "Pig{} received status response from pig{}".format(self.get_id(), message['pigID'])
            if self.get_id() == message['sender']:
                print "received status at request sender: Pig{} has {} hits left.".format(message['pigID'], message['status'])
            else:
                self._propagate_message(message, direction="backward")
            return
        elif message['action'] == 'request_status_all':
            print "Pig{} received status request for ALL pigs.".format(self.get_id())
            if self.get_id() == message['sender']:
                print "Pig{} received status of ALL pigs".format(self.get_id())
                print "Status: ", message['status']
            else:
                message['status'][str(self.get_id())] = self.status
                self._propagate_message(message)
            return
        if message['propagate']:
            self._propagate_message(message)
                
    def request_status(self, pigID):
        """
        Requests the status of the pig with the given pig ID.
        """
        print "Pig{} sending status request for pig{}.".format(self.get_id(), pigID)
        self.send_message({'sender' : self.get_id(), 'action' : 'request_status', 'propagate' : True, 'pigID' : pigID, 'status' : -1, 'hop_count' : 10})
        # status of -1 indicates unknown, i.e. it's a status request
        
    def request_status_all(self):
        """
        Requests the status of ALL pigs in the network.
        """
        print "Pig{} requested status from ALL pigs.".format(self.get_id())
        self.send_message({'sender': self.get_id(), 'action' : 'request_status_all', 'propagate' : True, 'status' : {str(self.get_id()) : self.status}, 'hop_count' : 10})