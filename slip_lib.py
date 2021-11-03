#!/usr/bin/env python3

# Created by Indraneel on 30/10/12

# SLIP decoder
class slip():

    def __init__(self):
        self.started = False
        self.escaped = False
        self.stream = bytearray()
        self.packet = bytearray()
        self.SLIP_END = bytes([0xC0])		# dec: 192
        self.SLIP_ESC = bytes([0xDB])		# dec: 219
        self.SLIP_ESC_END = bytes([0xDC])	# dec: 220
        self.SLIP_ESC_ESC = bytes([0xDD])	# dec: 221
        self.serialComm = None

    def appendData(self, chunk):
        self.stream += chunk

    def decode(self):
        packetlist = bytearray()
        for char in self.stream:
            char = bytes([char])
            # SLIP_END
            if char == self.SLIP_END:
                if self.started:
                    packetlist += self.packet
                else:
                    self.started = True
                self.packet = bytearray()
            # SLIP_ESC
            elif char == self.SLIP_ESC:
                self.escaped = True
            # SLIP_ESC_END
            elif char == self.SLIP_ESC_END:
                if self.escaped:
                    self.packet += self.SLIP_END
                    self.escaped = False
                else:
                    self.packet += char
            # SLIP_ESC_ESC
            elif char == self.SLIP_ESC_ESC:
                if self.escaped:
                    self.packet += self.SLIP_ESC
                    self.escaped = False
                else:
                    self.packet += char
            # all others
            else:
                if self.escaped:
                    raise Exception('SLIP Protocol Error')
                    self.packet = bytearray()
                    self.escaped = False
                else:
                    self.packet += char
                    self.started = True
        self.stream = bytearray()
        self.started = False
        return (packetlist)
        
    def encode(self, packet):
        # Encode an initial END character to flush out any data that 
        # may have accumulated in the receiver due to line noise
        encoded = bytearray(self.SLIP_END)
        for char in packet:
            char = bytes([char])
            # SLIP_END
            if char == self.SLIP_END:
                encoded +=  self.SLIP_ESC + self.SLIP_ESC_END
            # SLIP_ESC
            elif char == self.SLIP_ESC:
                encoded += self.SLIP_ESC + self.SLIP_ESC_ESC
            # the rest can simply be appended
            else:
                encoded += char
        encoded += self.SLIP_END
        return (encoded)