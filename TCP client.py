import socket


port=5050
host= '192.168.1.3'
address=(host, port)
format= "utf-8"
header= 64
disconnect_msg= "!!bYe!4!$//"

client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address)

def send(msg):
    message= msg.encode(format)
    msg_length= len(message)
    send_length= str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    client.send(send_length)
    client.send(message)


print(f"[CONNECTED] to {host}:{port}")
looped= True
while looped:
    msg=input("Do you want to send a message?(Y/N): ")
    if msg.capitalize()=="Y":
        send("I AM sending you a message ")
    else:
        send(disconnect_msg)
        looped= False