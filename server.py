import socket
import pickle
from threading import Thread
from main import main_jogo
from time import sleep as sl

def handle_client(conn):
    while True: # loop infinito caso reset tenha sido escolhido
        try:
            send_message(conn, "START_GAME") # envia a mensagem de inicio de jogo
            print("Sent start game message to the client.")

            message = pickle.loads(conn.recv(4096)) # mensagem retornada do cliente de inicio de jogo
            # loads para descriptografar a mensagem

            print("Received message from client:", message)

            if message == 'START':
                if reset := main_jogo(conn, 1):
                    sl(1)
                    continue
        except Exception as e:
            print(f"Error handling the client: {e}")
        break # caso reset não tenha sido escolhido, finaliza loop
    conn.close()

def send_message(conn, message):
    conn.sendall(pickle.dumps(message))

def start_server():
    host = "0.0.0.0"
    port = 5555

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print("Server waiting for connections...")

    while True:
        conn, addr = server.accept()
        print(f"Connection established with {addr}")

        Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    start_server()
