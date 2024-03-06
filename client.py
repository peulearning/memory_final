import socket
import pickle
from main import main_jogo
from time import sleep as sl

def main():
    host = input("Enter the server IP address: ")
    port = 5555

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((host, port))
        print("Connected to the server.")
        while True: # loop oara se caso reset tenha sido escolhido

            message = pickle.loads(client_socket.recv(4096)) # loads para descriptografar a mensagem
            
            print("Received message from server:", message)
            
            sl(1)
            client_socket.sendall(pickle.dumps('START')) # retorna pro servidor o inicio do jogo

            if message == 'START_GAME':
                print("Starting the game...")

                reset = main_jogo(client_socket, 2) # envia qual jogador é (no caso aqui, jogador 2)

                if reset: # se caso reset tiver sido escolhido, reinicia
                    continue

            else:
                print("Unexpected message from server:", message)

            break # se caso o reset não tiver sido escolhido, ele finaliza
    except Exception as e:
        print("Error connecting to the server:", e)

if __name__ == "__main__":
    main()
