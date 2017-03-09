# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 20:11:29 2017

@author: snoran
"""

import threading
import socket
import json
import Queue

exit_flag = 0

def receive_message(socket, callback = None):
    """
    Receives messages through the given socket and upon receiving messages, 
    passes them to the given callback, if provided.
    """
    while not exit_flag:
        message = socket.recv(1024)
        if message:
            if callback:
                callback(json.loads(message))
    
def send_message(socket, queue_lock, message_queue):
    """
    Safely sends messages from the given queue through the given socket.
    """
    while not exit_flag:                    
        queue_lock.acquire() # do we need this because it is the only thread accessing the queue?
        if not message_queue.empty():
            message = message_queue.get()
            socket.send(json.dumps(message))
        queue_lock.release()

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
    
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.address)
        self.server_socket.listen(5)
            
        print 'waiting for connection...'
        client, addr = self.server_socket.accept()
        print '...connected from:', addr
        
        threading.Thread(target=receive_message, args=(client, self.callback)).start()
        threading.Thread(target=send_message, args=(client, self.queue_lock, self.message_queue)).start()


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
    
    def run(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.address)
        self.client_socket.settimeout(3)
        
        threading.Thread(target=receive_message, args=(self.client_socket, self.callback)).start()
        threading.Thread(target=send_message, args=(self.client_socket, self.queue_lock, self.message_queue)).start()   

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
        self.response_queue = Queue.Queue()
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
        server_thread = ServerThread(self.address, self.response_queue, self.queue_lock, self.on_message_received)
        server_thread.start()
        self.connected_as_server = True # TODO only if successful
        
    def on_message_received(self, message):
        # do nothing, allow subclasses to override this
        print self.address, message
        return
        
    def send_message(self, message, direction = 'forward'):
        """
        Adds a message to the queue to be sent to the node's peer.
        
        Messages are by convention in JSON format. They consist of a 
        'content' field and a 'propagate' field, indicating whether it 
        should be relayed in the P2P network.
        
        """
        if direction == 'forward':
            if self.connected_as_client:
                self.queue_lock.acquire()
                self.message_queue.put(message)
                self.queue_lock.release()
            else:
                print "no node to send to"
        else:
            if self.connected_as_server:
                self.queue_lock.acquire()
                self.response_queue.put(message)
                self.queue_lock.release()
            else:
                print "no node to respond to"
                
if __name__=='__main__':     
    node1 = P2PNode(('localhost', 9001))
    node2 = P2PNode(('localhost', 9002))
    node1.connect(node2)
    node1.send_message({'content': 'this is a message'}, direction="forward")
    import time
    time.sleep(3)
    exit_flag=1