from src.server.Server import Server

if __name__ == '__main__':
    server = Server(5003, 5002, 5001)
    server.main()
