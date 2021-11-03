#!/usr/bin/env python3

# Created by Indraneel on 25/10/12

import socket

UDP_IP = "192.168.0.2"
UDP_PORT = 80
MESSAGE = b"Hello, World!"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

print("Message sent!")
msgFromServer = sock.recvfrom(1)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)