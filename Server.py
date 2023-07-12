import socket

def start_server():
    host = '127.0.0.1'
    port = 12345

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

start_server()
