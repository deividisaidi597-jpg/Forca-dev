import socket
import threading

clients = []

def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr}")

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            print("Recebido:", data)

            # depois vamos mandar pro event_bus
        except:
            break

    conn.close()


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print(f"Servidor rodando em {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()