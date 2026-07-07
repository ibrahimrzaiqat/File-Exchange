import socket
import time

# cd "C:\Users\Abo Al Cho5\Desktop\Ibrahim\Projects\File Transfer(FT)"

host= "255.255.255.255"
port= 12345
shouter_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

shouter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

msg=b'Hello, this is a broadcast message!'
while True:
    shouter_socket.sendto(msg, (host, port))
    print("Broadcast message sent!")
    time.sleep(5)
