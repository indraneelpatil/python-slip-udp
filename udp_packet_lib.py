#!/usr/bin/env python3

# Created by Indraneel on 30/10/12

import struct
from socket import socket, AF_PACKET, SOCK_RAW, IPPROTO_UDP, AF_INET
import socket

class udp_packet():

    def __init__(self,destAdd,destPort,payload,sourceAdd='192.168.0.3',sourcePort = 10000):
        self.sourceAdd = sourceAdd
        self.sourcePort = sourcePort
        self.destAdd = destAdd
        self.destPort = destPort
         #Check the type of data
        try:
            self.payload = payload.encode()
        except AttributeError:
            pass
        #self.payload = payload

        self.create_ipv4_feilds_list()

    def create_ipv4_feilds_list(self):
        # ---- [Internet Protocol Version] ----
        ip_ver = 4
        ip_vhl = 5

        self.ip_ver = (ip_ver << 4 ) + ip_vhl

        # ---- [ Differentiate Servic Field ]
        ip_dsc = 0
        ip_ecn = 0

        self.ip_dfc = (ip_dsc << 2 ) + ip_ecn

        # ---- [ Total Length]
        self.ip_tol = 0

        # ---- [ Identification ]
        self.ip_idf = 54321

        # ---- [ Flags ]
        ip_rsv = 0
        ip_dtf = 0
        ip_mrf = 0
        ip_frag_offset = 0

        self.ip_flg = (ip_rsv << 7) + (ip_dtf << 6) + (ip_mrf << 5) + (ip_frag_offset)

        # ---- [ Total Length ]
        self.ip_ttl = 255

        # ---- [ Protocol ]
        self.ip_proto = IPPROTO_UDP

        # ---- [ Check Sum ]
        self.ip_chk = 0

        # ---- [ Source Address ]
        self.ip_saddr = socket.inet_aton(self.sourceAdd)

        # ---- [ Destination Address ]
        self.ip_daddr = socket.inet_aton(self.destAdd)

    def assemble_ipv4_feilds(self):
        self.raw = struct.pack('!BBHHHBBH4s4s' , 
        self.ip_ver,   # IP Version 
        self.ip_dfc,   # Differentiate Service Feild
        self.ip_tol,   # Total Length
        self.ip_idf,   # Identification
        self.ip_flg,   # Flags
        self.ip_ttl,   # Time to leave
        self.ip_proto, # protocol
        self.ip_chk,   # Checksum
        self.ip_saddr, # Source IP 
        self.ip_daddr  # Destination IP
        )
        return self.raw

    def assemble_udp_header(self):
        payload_len = len(self.payload)
        udp_length = 8 + payload_len
        checksum = 0
        pseudo_header = struct.pack('!BBH', 0, IPPROTO_UDP, udp_length)
        pseudo_header = self.ip_saddr + self.ip_daddr + pseudo_header
        udp_header = struct.pack('!4H', self.sourcePort, self.destPort, udp_length, checksum)

        checksum = self.checksum_func(pseudo_header + udp_header + self.payload)

        return struct.pack('!4H', self.sourcePort, self.destPort, udp_length, checksum)

    def checksum_func(self,data):
        checksum = 0
        data_len = len(data)
        if (data_len % 2):
            data_len += 1
            data += struct.pack('!B', 0)
        
        for i in range(0, data_len, 2):
            w = (data[i] << 8) + (data[i + 1])
            checksum += w

        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum = ~checksum & 0xFFFF
        return checksum

    def construct(self):
        self.ip_header = self.assemble_ipv4_feilds()
        self.udp_header = self.assemble_udp_header()
        packet = self.ip_header + self.udp_header + self.payload
        # update length and checksum of IP packet
        self.ip_tol = len(packet)
        #self.ip_chk = self.checksum_func(self.ip_header)
        print('[UDP_Packet_Lib] Packed a packet of length :{}'.format(self.ip_tol))
        self.ip_header = self.assemble_ipv4_feilds()

        return self.ip_header + self.udp_header + self.payload



if __name__=='__main__':
    serverAddressPort = ("127.0.0.1", 20001)
    udp_obj = udp_packet(serverAddressPort[0],serverAddressPort[1],'Hello from lib')
    udp_data = udp_obj.construct()
    print(udp_data)

    # Send packet to udp server
    s = socket.socket(AF_INET, SOCK_RAW,IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    #s.bind(("lo",0))
    
    #s.send(udp_data)
    s.sendto(udp_data, serverAddressPort)
    #s.connect(serverAddressPort)
    print("Connected!")
    
    message = s.recvfrom(4096)
    print(message)
    #print(message.decode('hex'))
