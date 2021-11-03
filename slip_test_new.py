#!/usr/bin/env python3

# Created by Indraneel on 30/10/12

import serial
import threading
from time import sleep
from pyftdi.ftdi import Ftdi
import pyftdi.serialext
import json

from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from slip_lib import slip
from udp_packet_lib import udp_packet
from bitstring import BitArray

Ftdi.show_devices() 

global FTDIPort, SerialPort,packet_dict

#SerialPort = pyftdi.serialext.serial_for_url('ftdi://ftdi:232:AB0LPYKJ/1', baudrate=9600)
SerialPort = serial.Serial('/dev/ttyUSB0', 9600, parity=PARITY_NONE,timeout=None,bytesize=EIGHTBITS,stopbits=STOPBITS_ONE)

loop_back_test = False

def serial_receive(loopback_cv):
    global SerialPort, loop_back_test
    print("Listening on serial")
    # Create decoding object
    slip_obj = slip()
    if(loop_back_test):
        loopback_cv.acquire()
        loopback_cv.notifyAll()
        loopback_cv.release()
    while (1):
        
        # Wait until there is data waiting in the serial buffer
        #if(SerialPort.in_waiting > 0):

        # Read data out of the buffer until a carraige return / new line is found
        serialByte = SerialPort.read()
        slip_obj.appendData(serialByte)
        # Check if full packet received
        if(serialByte == slip_obj.SLIP_END):
            decoded_packet = slip_obj.decode()
            if(len(decoded_packet)>1):

                # Print the contents of the serial data
                print('*****************************************************************')
                print('Received {} bytes'.format(len(decoded_packet)))
                print('*****************************************************************')
                try:
                    print(decoded_packet.hex())
                    #print(serialString.decode('Ascii'))
                except:
                    print(decoded_packet)
                if(loop_back_test):
                    loopback_cv.acquire()
                    loopback_cv.notifyAll()
                    loopback_cv.release()
    
            else:
                # Reject decoded packet
                pass


def slip_test(loopback_cv):
    global SerialPort, loop_back_test
    print("Starting slip test!")
    num = 0
    loopback_cv.acquire()
    while(1):
        if(loop_back_test):
            loopback_cv.wait()
            print("Sending packet {}".format(num))
            num =num+1
            sleep(0.01)
        else:
            print("Press enter to send packet!")
            input()
        try:
            print(" ")
            serverAddressPort = ("192.168.0.2", 80)
            udp_obj = udp_packet(serverAddressPort[0],serverAddressPort[1],'Moonranger')
            #test = b'\xf0\xf0\xf0'
            udp_data = bytearray(udp_obj.construct())
            udp_slip_data =  slip().encode((udp_data))
            print("Sending packet :",udp_slip_data.hex())
            it = 0
            for byte in udp_slip_data:
                it = it+1
                SerialPort.write(bytes([byte]))
                #print(byte)
                sleep(0.005)
            print('Sent {} bytes!'.format(it))
        except Exception as e:
            print("Check packet name! "+str(e))

        
          
   

if __name__ == "__main__": 
    loopback_cond = threading.Condition()
    thread = threading.Thread(target = slip_test, args = (loopback_cond, )) 
    thread.start()
    serial_receive(loopback_cond)
    thread.join() 
    print("Slip test ...exiting") 