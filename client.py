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

import threading
import time
import socket
import Queue
import json
import numpy as np

exit_flag = 0

class ServerThread(threading.Thread):
    """
    The server thread is responsible for accepting client connections 
    and receiving data from connected nodes. We only expect a single 
    client node.
    """
    def __init__(self, address, message_queue, queue_lock, callback = None):
        threading.Thread.__init__(self)
        self.address = address
        self.message_queue = message_queue
        self.queue_lock = queue_lock
        self.callback = callback
        self.client = None
        
    def receive_message(self):
        while not exit_flag:
            message = self.client.recv(1024)
            if message:
                if self.callback:
                    self.callback(json.loads(message))
        
    def send_message(self):
        while not exit_flag:                    
            self.queue_lock.acquire() # do we need this because it is the only thread accessing the queue?
            if not self.message_queue.empty():
                message = self.message_queue.get()
                self.client.send(json.dumps(message))
                self.queue_lock.release()
            else:
                self.queue_lock.release()
    
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.address)
        self.server_socket.listen(5)
            
        print 'waiting for connection...'
        self.client, addr = self.server_socket.accept()
        print '...connected from:', addr
        
        threading.Thread(target=self.receive_message).start()
        threading.Thread(target=self.send_message).start()


class ClientThread(threading.Thread):
    """
    The client thread is responsible for connecting to the node specified 
    by the given address and sending data to that node.
    """
    def __init__(self, address, message_queue, queue_lock, callback = None):
        threading.Thread.__init__(self)
        self.address = address
        self.message_queue = message_queue
        self.queue_lock = queue_lock
        self.callback = callback
        
    def receive_message(self):
        while not exit_flag:
            message = self.client_socket.recv(1024)
            if message:
                if self.callback:
                    self.callback(json.loads(message))
        
    def send_message(self):
        while not exit_flag:                    
            self.queue_lock.acquire() # do we need this because it is the only thread accessing the queue?
            if not self.message_queue.empty():
                message = self.message_queue.get()
                self.client_socket.send(json.dumps(message))
                self.queue_lock.release()
            else:
                self.queue_lock.release()
    
    def run(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.address)
        self.client_socket.settimeout(3)
        
        threading.Thread(target=self.receive_message).start()
        threading.Thread(target=self.send_message).start()        
        
#        while not exit_flag:                    
#            self.queue_lock.acquire() # do we need this because it is the only thread accessing the queue?
#            if not self.message_queue.empty():
#                message = self.message_queue.get()
#                self.client_socket.send(json.dumps(message))
#                self.queue_lock.release()
#            else:
#                self.queue_lock.release()

class P2PNode():
    """
    Represents a node in a peer-to-peer network. The network is a circular, 
    singly-connected network, that is each node is connected to exactly two 
    other nodes in the network. Thus each node acts as both a client and 
    server.
    
    """
    def __init__(self, address):
        self.address = address
        self.message_queue = Queue.Queue()
        self.queue_lock = threading.Lock()
        self.connected_as_client = False
        self.connected_as_server = False
    
    def connect(self, peer):
        """
        Connects to the given P2PNode peer.
        """
        peer.listen()
        client_thread = ClientThread(peer.address, self.message_queue, self.queue_lock, self.on_message_received)
        client_thread.start()
        self.connected_as_client = True # TODO only if successful
        
    def listen(self):
        """
        Sets up a server socket, which listens for connection attempts 
        by other nodes.
        """
        print "starting server thread with address " + str(self.address)
        server_thread = ServerThread(self.address, self.message_queue, self.queue_lock, self.on_message_received)
        server_thread.start()
        self.connected_as_server = True # TODO only if successful
        
    def on_message_received(self, message):
        # do nothing, allow subclasses to override this
        return
        
    def send_message(self, message):
        """
        Adds a message to the queue to be sent to the node's peer.
        
        Messages are by convention in JSON format. They consist of a 
        'content' field and a 'propagate' field, indicating whether it 
        should be relayed in the P2P network.
        
        """
        if self.connected_as_client:
            self.queue_lock.acquire()
            self.message_queue.put(message)
            self.queue_lock.release()
        else:
            print "no node to send to"
        
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
exit_flag = 1

# we'll work with a 5 x 5 grid to start
grid = np.zeros((5,5))

for pig in pigs:
    grid[pig.location] = pig.get_id()
    if pig.location == bird_landing:
        pig.status -= 1
        
for pig in pigs:
    print pig.get_id(), pig.status
    
print grid
#node1 = P2PNode(('localhost', 9999))
#node2 = P2PNode(('localhost', 8888))
#
#node1.connect(node2)