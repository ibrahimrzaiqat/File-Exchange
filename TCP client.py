import socket

# cd "C:\Users\Abo Al Cho5\Desktop\Ibrahim\Projects\File Transfer(FT)"

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
    user_input=input("Do you want to send a message?(Type it/ d to disconnect): ")
    if user_input.capitalize()=="D":
        send(disconnect_msg)
        looped= False
        
    else:
        send(user_input)