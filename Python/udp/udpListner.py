import socket

serverAddressPort   = ("127.0.0.1", 20001)

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


msgFromServer = UDPClientSocket.recvfrom()

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)