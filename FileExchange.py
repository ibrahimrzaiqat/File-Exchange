#BACKEND IMPORTS
import os
import socket
import threading
import json
#FRONTEND IMPORTS
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
     QVBoxLayout, QWidget, QLabel, QListWidget,
      QProgressBar, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from os.path import basename, getsize


# cd "C:\Users\Abo Al Cho5\Desktop\Ibrahim\Projects\File Transfer(FT)"


#VARIABLES
udp_port=12345
tcp_port=12346
host='0.0.0.0'
udp_address=(host, udp_port)
tcp_address=(host, tcp_port)
format= "utf-8"
header= 1024
disconnect_msg= "!!bYe!4!$//"
my_ip= socket.gethostbyname(socket.gethostname())

class UDPListenerThread(QThread):
    device_discovered = pyqtSignal(str, str) 
    
    def run(self):
        listener_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener_socket.bind(udp_address)

        while True:
            data, add= listener_socket.recvfrom(1024) 
            sender_ip= add[0]
            sender_port= add[1]
            if sender_ip != my_ip:
                decoded_message= data.decode("utf-8")
                print(f"Received message from {sender_ip}:{sender_port}: {decoded_message}")
                device_name= decoded_message
                self.device_discovered.emit(device_name, sender_ip)


class TCPServerThread(QThread):
    receive_progress_signal = pyqtSignal(int)  # Signal to update progress bar
    download_complete_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_canceled= False
        self.downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(self.downloads_dir, exist_ok=True)

    def get_unique_path(self, filename):
        base, ext = os.path.splitext(filename)
        candidate = os.path.join(self.downloads_dir, filename)
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(self.downloads_dir, f"{base} ({counter}){ext}")
            counter += 1
        return candidate

    def run(self):
        server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(tcp_address)
        server_socket.listen(5)
        server_socket.settimeout(1.0)

        while True:
            try:
                connection, addr= server_socket.accept()
                thread= threading.Thread(target=self.handle_client, args=(connection, addr))
                thread.daemon= True
                thread.start()
            except socket.timeout:
                continue

    def handle_client(self,conn, addr):
        self.is_canceled=False
        connected=True
        while connected:
            message= conn.recv(header).decode(format).strip()
            if not message or message ==disconnect_msg:
                break #when connection with client a "blank" msg is sent that will be interpreted as a false value, so the connection will be closed
            data=json.loads(message)
            msg_length= int(data["file_size"])
            msg_name= basename(data["file_name"])
            save_path= self.get_unique_path(msg_name)
            bytes_received = 0
            with open(save_path, 'wb') as f:
                while bytes_received < msg_length:
                    chunk = conn.recv(1024)
                    if not chunk or self.is_canceled==True:  
                        break
                    f.write(chunk)
                    bytes_received += len(chunk)
                    self.receive_progress_signal.emit(int((bytes_received / msg_length) * 100))
            if self.is_canceled:
                os.remove(save_path)
            else:
                self.download_complete_signal.emit(basename(save_path))

        conn.close()

class TCPClientThread(QThread):
    sender_progress_signal = pyqtSignal(int)
    send_complete_signal= pyqtSignal(str)
    def __init__(self, target_ip, file_path):
        super().__init__()
        self.target_ip= target_ip
        self.file_path= file_path
        self.is_canceled= False

    def run(self):
        client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.target_ip, tcp_port))

        message= {"file_name": os.path.basename(self.file_path) , "file_size": os.path.getsize(self.file_path)}
        data= json.dumps(message).encode(format)
        data += b' ' * (header - len(data))
        client_socket.send(data)

        file_size = os.path.getsize(self.file_path)
        bytes_sent = 0
        self.is_canceled=False
        with open(self.file_path, 'rb') as f:    
            while bytes_sent < file_size:
                chunk = f.read(1024)
                if not chunk or self.is_canceled==True:
                    break
                client_socket.send(chunk)
                bytes_sent += len(chunk)
                self.sender_progress_signal.emit(int((bytes_sent / file_size) * 100))
        client_socket.send(disconnect_msg.encode(format))
        client_socket.close()

        if not self.is_canceled:
            self.send_complete_signal.emit(os.path.basename(self.file_path))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.resize(800, 700)

        self.target_ip= None
        self.file_path= None   

        self.known_devices={} 

        self.setAcceptDrops(True)  # Enable drag and drop
        # Create the central widget and set it
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create the layout
        self.layout = QVBoxLayout()

        # 1. Status Label
        self.status_label = QLabel(f"🟢 Status: Listening on {host}:{udp_port}")
        self.layout.addWidget(self.status_label)
        
        
        # 2. Device List
        self.layout.addWidget(QLabel("Available Devices on LAN:"))
        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.on_device_selected)
        self.layout.addWidget(self.device_list)

        # 3. Drag and Drop Area
        self.drop_area = QLabel("📂 Drag & Drop File Here")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px; padding: 30px;")
        self.layout.addWidget(self.drop_area)

        # 4. File Info & Progress Bar
        self.file_label = QLabel("Selected File: None")
        self.layout.addWidget(self.file_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0) # Starts at 0%
        self.layout.addWidget(self.progress_bar)

        # 5. Buttons (Horizontal Layout)
        self.button_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send File")
        self.cancel_btn = QPushButton("Cancel")
        self.button_layout.addWidget(self.send_btn)
        self.button_layout.addWidget(self.cancel_btn)
        self.send_btn.clicked.connect(self.send_btn_clicked)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)
        self.layout.addLayout(self.button_layout)

        
        self.central_widget.setLayout(self.layout)

        self.udp_thread= UDPListenerThread()
        self.udp_thread.device_discovered.connect(self.add_device_to_list)
        self.udp_thread.start()

        self.tcp_server_thread= TCPServerThread()
        self.tcp_server_thread.receive_progress_signal.connect(self.progress_bar.setValue)
        self.tcp_server_thread.download_complete_signal.connect(self.download_complete)
        self.tcp_server_thread.start()

        self.shout_timer= QTimer(self)
        self.shout_timer.timeout.connect(self.send_udp_shout)
        self.shout_timer.start(5000)



    def send_udp_shout(self):
        shouter_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        shouter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        msg_name= socket.gethostname().encode(format)   
        
        shouter_socket.sendto(msg_name, ("255.255.255.255", udp_port))

    def send_btn_clicked(self):
        if not self.target_ip or not self.file_path:
            self.status_label.setText("⚠️ Please select a device and a file before sending.")
            return

        self.status_label.setText(f"📤 Sending {basename(self.file_path)} to {self.target_ip}...")
        self.tcp_client_thread= TCPClientThread(self.target_ip, self.file_path)
        self.tcp_client_thread.sender_progress_signal.connect(self.progress_bar.setValue)
        self.tcp_client_thread.send_complete_signal.connect(self.on_send_complete)
        self.tcp_client_thread.start()

    def cancel_btn_clicked(self):
        if hasattr(self, 'tcp_client_thread') and self.tcp_client_thread.isRunning():
            self.tcp_client_thread.is_canceled= True
            self.status_label.setText("⚠️ File transfer canceled.")
        elif hasattr(self, 'tcp_server_thread') and self.tcp_server_thread.isRunning():
            self.tcp_server_thread.is_canceled= True
            self.status_label.setText("⚠️ File reception canceled.")
        else:
            self.status_label.setText("⚠️ No active file transfer to cancel.")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            files= [url.toLocalFile() for url in event.mimeData().urls()]
            if files:
                file_path= files[0]
                
                print(f"File dropped: {file_path}")
                self.on_file_selected(file_path)

    def closeEvent(self, event):
        self.shout_timer.stop()

        QApplication.quit()

        event.accept()
        
    def on_file_selected(self, file_path):
        self.file_path = file_path 
        filename= basename(file_path)
        filesize= getsize(file_path)
        if filesize > 1024*1024:
            size_str= f"{filesize / (1024*1024):.2f} MB"
        else:
            size_str= f"{filesize / 1024:.2f} KB"
        self.file_label.setText(f"Selected File: {filename}")
        self.status_label.setText(f"🟢 File Loaded: {filename} ({size_str})")
        print(f"[UI UPDATE] Displaying selected file: {filename}")

        self.progress_bar.setValue(0)  

    def add_device_to_list(self, name, ip):
        if ip not in self.known_devices:
            self.known_devices[ip]= name
            self.device_list.addItem(f"{name} ({ip})")
            print(f"[UI UPDATE] Added device to list: {name} ({ip})")

    def progress_bar_update(self, value):
        self.progress_bar.setValue(value)
    
    def on_device_selected(self, item):
        device_info= item.text()
        ip_start= device_info.find('(') + 1
        ip_end= device_info.find(')')
        self.target_ip= device_info[ip_start:ip_end]
        self.status_label.setText(f"🟢 Selected Device: {device_info}")
        print(f"[UI UPDATE] Selected device: {device_info}")


    def download_complete(self, filename):
        self.status_label.setText(f"✅ Download complete: {filename}")
        self.progress_bar.setValue(0)
        print(f"[UI UPDATE] Download complete: {filename}")


    def on_send_complete(self, filename):
        self.status_label.setText(f"✅ Sent: {filename}")
        self.progress_bar.setValue(0)
        self.file_path = None
        self.file_label.setText("Selected File: None")
        print(f"[UI UPDATE] Send complete: {filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.send_udp_shout()  # Send the initial UDP shout when the application starts
    sys.exit(app.exec_())