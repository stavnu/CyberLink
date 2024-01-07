import io
import socket
import struct
import threading

import keyboard
import pyautogui
from pynput.mouse import Controller, Button

from src.protocol.Protocol import recvall
from src.server.Server import MouseCommands


class Client:
    def __init__(self, server_ip, screen_port, mouse_port, keyboard_port):
        self.server_ip = server_ip  # paste your server ip address here
        self.screen_port = screen_port
        self.mouse_port = mouse_port
        self.keyboard_port = keyboard_port
        self.screen_socket = socket.socket()
        self.mouse_socket = socket.socket()
        self.keyboard_socket = socket.socket()
        self.connect_to_server()
        self.mouse = Controller()
        self.run = True

    def connect_to_server(self):
        try:
            self.screen_socket.connect((self.server_ip, self.screen_port))
            self.mouse_socket.connect((self.server_ip, self.mouse_port))
            self.keyboard_socket.connect((self.server_ip, self.keyboard_port))
        except Exception as e:
            print("Error with connection", e)
            self.run = False
        else:
            print("Connected to server")

    # def send_message_to_server(client_socket, message):
    #     print("Sending")
    #     client_socket.sendall(message.encode())
    #
    #
    # def print_pressed_keys(key, client_socket):
    #     print("Pressed: ", key.name)
    #     message = f"Key pressed: {key.name}"
    #     send_message_to_server(client_socket, message)

    def handle_screen_sharing(self):
        while self.run:
            try:
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
                self.screen_socket.sendall(data)

            except (socket.error, BrokenPipeError):
                # Handle socket errors, set run to False, and break out of the loop
                self.run = False
                break

    def keyboard_controlled(self):
        while self.run:
            key = self.keyboard_socket.recv(1024).decode()
            if key:
                print("Press key - > ", key)
                keyboard.press_and_release(key)
            else:
                print("connection lost with server")
                self.keyboard_socket.close()
                self.run = False

    def handle_mouse_control(self):
        while self.run:
            data = recvall(self.mouse_socket, 12)  # Increase size to accommodate the command
            new_mouse_pos = struct.unpack('!II', data[0:8])
            command_value = struct.unpack('!I', data[8:])[0]
            new_command = MouseCommands(command_value)

            # Move mouse to new position
            self.mouse.position = (new_mouse_pos[0], new_mouse_pos[1])

            # Handle mouse commands on the client side
            if new_command == MouseCommands.LEFT_HOLD:
                # print("Left button held down")
                self.mouse.press(Button.left)
            elif new_command == MouseCommands.RIGHT_CLICK:
                # print("Right button clicked")
                self.mouse.click(Button.right)
            elif new_command == MouseCommands.MIDDLE_CLICK:
                # print("Middle button clicked")
                self.mouse.click(Button.middle)
            # elif new_command == MouseCommands.X1_CLICK:
            #     # print("X1 button clicked")
            #     self.mouse.click(Button.x1)
            # elif new_command == MouseCommands.X2_CLICK:
            #     # print("X2 button clicked")
            #     self.mouse.click(Button.x2)
            elif new_command == MouseCommands.LEFT_RELEASE:
                # print("Left button released")
                self.mouse.release(Button.left)
            elif new_command == MouseCommands.SCROLL_UP:
                # print("scroll up")
                pyautogui.scroll(1)
            elif new_command == MouseCommands.SCROLL_DOWN:
                # print("scroll down")
                pyautogui.scroll(-1)
            # else:
            # print("no command")
            new_command = MouseCommands.NOOP

    # def keylogger():
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     port = 5000
    #     connection_successful = False
    #     s.connect((server_ip, port))
    #     print("Connected")
    #     connection_successful = True
    #
    #     def on_key_pressed(key):
    #         print_pressed_keys(key, s)
    #
    #     keyboard.on_press(on_key_pressed)
    #     if not connection_successful:
    #         print("Failed to connect to the server")
    #         s.close()
    #         sys.exit()
    #     keyboard.wait('esc')
    #     s.close()

    def main(self):
        # keylogger()
        # keyboard_controlled()
        # mouse_controlled()
        # send_screenshot()
        t1 = threading.Thread(target=self.handle_screen_sharing)
        t2 = threading.Thread(target=self.handle_mouse_control)
        t3 = threading.Thread(target=self.keyboard_controlled)
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

    if __name__ == "__main__":
        main()
