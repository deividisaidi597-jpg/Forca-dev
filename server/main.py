from dotenv import load_dotenv
from server.database.connection import DatabaseConnection
from server.network.socket_server import SocketServer

def main():
    # 1. Load variables from .env
    load_dotenv()

    # 2. Connect to the database and create collection if it doesn't exist
    print("Starting database connection...")
    DatabaseConnection.connect()

    # 3. Start the Socket server to listen for clients
    server = SocketServer()
    server.start()

if __name__ == "__main__":
    main()