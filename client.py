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

class ServerThread(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.address = address
    
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.address)
        self.server_socket.listen(5)
            
        print 'waiting for connection...'
        cs, addr = self.server_socket.accept()
        print '...connected from:', addr
        while True:
            message = cs.recv(1024)
            if message:
                print "received: " + str(message)

class ClientThread(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.address = address
    
    def run(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.address)
        time.sleep(2)
        self.client_socket.send("hello")

class P2PNode():
    """
    Represents a node in a peer-to-peer network. The network is a circular, 
    singly-connected network, that is each node is connected to exactly two 
    other nodes in the network. Thus each node acts as both a client and 
    server.
    
    """
    def __init__(self, address):
        self.address = address
    
    def connect(self, peer):
        peer.listen()
        client_thread = ClientThread(peer.address)
        client_thread.start()
        
    def listen(self):
        print "starting server thread with address " + str(self.address)
        server_thread = ServerThread(self.address)
        server_thread.start()
        
node1 = P2PNode(('localhost', 9999))
node2 = P2PNode(('localhost', 8888))

node1.connect(node2)