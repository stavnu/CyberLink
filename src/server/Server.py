import enum
import io
import socket
import struct
import threading
import time

import tkinter as tk
import keyboard
from PIL import Image, ImageTk, ImageDraw
from pynput.mouse import Controller, Listener, Button

from src.protocol.Protocol import recvall


class MouseCommands(enum.Enum):
    NOOP = 0
    LEFT_CLICK = 1
    RIGHT_CLICK = 2
    MIDDLE_CLICK = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5
    LEFT_HOLD = 6
    LEFT_RELEASE = 7
    # X1_CLICK = 8
    # X2_CLICK = 9


class Server:
    is_focused = False
    run = True
    last_command = MouseCommands.NOOP

    def __init__(self, screen_port, mouse_port, keyboard_port):
        self.t2 = None
        self.t1 = None
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.screen_port = screen_port
        self.mouse_port = mouse_port
        self.keyboard_port = keyboard_port
        self.screen_socket = socket.socket()
        self.mouse_socket = socket.socket()
        self.keyboard_socket = socket.socket()
        self.bind_sockets()
        self.listen_sockets()
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=300, height=300)
        self.canvas.pack()
        self.mouse = Controller()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.run = False
        if self.t1:
            self.t1.join()
        self.root.destroy()

    def bind_sockets(self):
        try:
            self.screen_socket.bind((self.host_ip, self.screen_port))
            self.mouse_socket.bind((self.host_ip, self.mouse_port))
            self.keyboard_socket.bind((self.host_ip, self.keyboard_port))
        except Exception as e:
            print("Failed to bind", e)
        else:
            print("Binded successfully")

    def listen_sockets(self):
        self.screen_socket.listen()
        self.mouse_socket.listen()
        self.keyboard_socket.listen()

    # todo:
    # def start_keylogger_listener():
    #     port = 5000
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.bind((host_ip, port))
    #         s.listen(1)
    #         print("Server listening on " + host_ip + ":" + str(port))
    #         conn, addr = s.accept()
    #         # addr[1] is the port
    #         print("Connected by ", addr[0], " Port : ", addr[1])
    #         while True:
    #             data = conn.recv(1024)
    #             if not data:
    #                 break
    #             keylogger = data.decode()
    #             print("Key hit : ", keylogger)
    #         print("Client disconnected.")
    def update_focus_state(self):
        if not self.root.winfo_exists():
            return
        self.is_focused = self.root.focus_displayof() is not None

    def start_keyboard_control(self):
        keyboard_socket, addr = self.keyboard_socket.accept()
        print("Keyboard service connected ", {addr})
        while self.run:
            key = keyboard.read_event()
            if key.event_type == keyboard.KEY_DOWN:
                key_name = key.name
                # print(f"Key pressed: {key_name}")
                message = key_name
                if self.is_focused:
                    keyboard_socket.sendall(message.encode())

    def start_mouse_control(self):
        try:
            with Listener(on_scroll=self.on_scroll, on_click=self.on_click):
                mouse_socket, addr = self.mouse_socket.accept()
                print('Mouse service connected :', addr)
                while self.run:
                    if self.is_focused:
                        new_mouse_pos = self.mouse.position
                        command = self.detect_mouse_command()
                        data = struct.pack('!III', int(new_mouse_pos[0]), int(new_mouse_pos[1]), command.value)
                        mouse_socket.sendall(data)
                        self.last_command = MouseCommands.NOOP
                    time.sleep(0.001)
        except ConnectionResetError:
            print("ConnectionResetError: Connection forcibly closed by the remote host")
            self.run = False
            self.on_close()

    def detect_mouse_command(self):
        return getattr(self, 'last_command', MouseCommands.NOOP)

    def on_scroll(self, x, y, dx, dy):
        if not self.is_focused:
            return
        if dy > 0:
            self.last_command = MouseCommands.SCROLL_UP
            # print("scrolled up")
        elif dy < 0:
            self.last_command = MouseCommands.SCROLL_DOWN
            # print("scrolled down")
        else:
            self.last_command = MouseCommands.NOOP

    def on_click(self, x, y, button, pressed):
        if not self.is_focused:
            return
        if pressed:
            if button == Button.left:
                # print("Left button held down")
                self.last_command = MouseCommands.LEFT_HOLD
            elif button == Button.right:
                # print("Right button clicked")
                self.last_command = MouseCommands.RIGHT_CLICK
            elif button == Button.middle:
                # print("Middle button clicked")
                self.last_command = MouseCommands.MIDDLE_CLICK
            # elif button == Button.x1:
            #     # print("X1 button clicked")
            #     self.last_command = MouseCommands.X1_CLICK
            # elif button == Button.x2:
            #     # print("X2 button clicked")
            #     self.last_command = MouseCommands.X2_CLICK
        else:
            if button == Button.left:
                # print("Left button released")
                self.last_command = MouseCommands.LEFT_RELEASE
            else:
                # print("Button released")
                self.last_command = MouseCommands.NOOP

    def receive_screenshot(self):
        print('HOST IP:', self.host_ip)
        # Socket Accept
        server_socket, addr = self.screen_socket.accept()
        print("Screen service connected  : ", addr)
        if server_socket:
            while self.run:
                self.update_focus_state()
                # Receive mouse position, length of byte array and byte array
                data = recvall(server_socket, 12)

                if data is not None:  # Check if data is not None
                    # Unpack data only if it is not None
                    mouse_pos = struct.unpack('!II', data[:8])
                    length = struct.unpack('!I', data[8:12])[0]
                    b = recvall(server_socket, length)

                    # Convert byte array to image
                    image = Image.open(io.BytesIO(b))

                    # Draw cursor on image
                    draw = ImageDraw.Draw(image)
                    draw.ellipse((mouse_pos[0] - 5, mouse_pos[1] - 5, mouse_pos[0] + 5, mouse_pos[1] + 5), fill='red')

                    # Display image
                    imgtk = ImageTk.PhotoImage(image=image)
                    self.canvas.config(width=imgtk.width(), height=imgtk.height())
                    self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
                    self.root.update()

    def main(self):
        # start_mouse_control()
        # start_keyboard_control()
        # start_keylogger_listener()
        # receive_screenshot()
        self.t1 = threading.Thread(target=self.start_mouse_control, name="MouseControlThread")
        self.t1.start()
        self.t2 = threading.Thread(target=self.start_keyboard_control, name="KeyboardControlThread")
        self.t2.start()
        # Update the focus state every 100 milliseconds
        self.root.after(100, self.update_focus_state)
        self.receive_screenshot()
