import socket
import sys
import os
import binascii
import struct

def twos_comp_two_bytes(msb, lsb):
    return struct.unpack('>h', bytes([msb, lsb]))[0]  
    #return struct.unpack('<h', bytes([lsb, msb]))[0] # different order `[lsb, msb]`
    #return struct.unpack( 'h', bytes([lsb, msb]))[0] # different order `[lsb, msb]`
    print(twos_comp_two_bytes(0b11111101, 0b11001001))

localIP     = "192.168.11.105"
localPort   = 10561

bufferSize  = 1400

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 # Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

def fetch_data(msg):
    for i in range(len(msg)-1):  
        data_type = twos_comp_two_bytes(msg[i],msg[i+1])
        if((data_type > 4999) and (data_type < 5011)):
            data_length = twos_comp_two_bytes(msg[i+2],msg[i+3])
            output = msg[i+4 : i+4+int(data_length)] 
            print("Type : ", data_type, " length :", data_length , end = " value : ")
            for z in range(len(output)):
                print(hex(output[z]) ,end = " " )
            print("")
        i += 2
 

# Listen for incoming datagrams
def main ():
    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        print("\n\n",clientIP)
        fetch_data(message)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

