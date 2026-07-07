import socket
import threading 

port=5050
host= socket.gethostbyname(socket.gethostname())
address=(host, port)
format= "utf-8"
header= 64
disconnect_msg= "!!bYe!4!$//"


server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)

def handle_client(conn, addr):

    connected=True
    while connected:
        msg_length= conn.recv(header).decode(format)
        if msg_length:#when connection with client a "blank" msg is sent that will be interpreted as a false value, so the connection will be closed
            msg_length= int(msg_length)
            msg=conn.recv(msg_length).decode(format)
            if msg== disconnect_msg:
                connected=False
            print(f"[{addr}]: {msg}")
    conn.close()


def start():
    server.listen(5)
    while True:
        connection, addr= server.accept()
        thread= threading.Thread(target= handle_client, args=(connection, addr))
        thread.daemon= True
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print(f"[STARTING SERVER]")
start()
