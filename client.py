# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:55:32 2017

@author: snoran
"""

import socket

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# now connect to the web server on port 80 - the normal http port
s.connect(("localhost", 9999))