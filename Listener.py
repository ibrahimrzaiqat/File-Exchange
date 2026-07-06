import socket 

host= "0.0.0.0"
port= 12345
#inet is internet socket, type of internet socket is datagram socket(UDP)
listener_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listener_socket.bind((host, port))# binds to specific address and port number, if no address is specified it binds to all available interfaces


while True:
    data, address= listener_socket.recvfrom(1024) 
    #adress is a tuple containing the sender's IP address and port number (ip addrress, port), data is the message received from the sender
    sender_ip= address[0]
    sender_port= address[1]
    decoded_message= data.decode("utf-8")
    print(f"Received message from {sender_ip}:{sender_port}: {decoded_message}")
    