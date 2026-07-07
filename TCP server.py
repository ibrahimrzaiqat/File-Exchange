import socket
import threading 


port=5050
host= '0.0.0.0'
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
    server.settimeout(1.0)
    print(f"[STARTING SERVER]")

    while True:
        try:
            connection, addr= server.accept()
            thread= threading.Thread(target= handle_client, args=(connection, addr))
            thread.daemon= True
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except socket.timeout:
            continue

try:
    start()
except KeyboardInterrupt:
    print(f"[SHUTTING DOWN SERVER]")
    server.close()
