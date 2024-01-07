from src.client.Client import Client

if __name__ == "__main__":
    client = Client('10.100.102.149', 5003, 5002, 5001)
    client.main()
