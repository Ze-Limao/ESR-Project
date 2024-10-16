import socket, sys, signal
from functools import partial


def ctrl_slash_handler(sig,frame):
    print("\n Exiting server")
    sys.exit(0)

def start_server(host='10.0.0.10', port=8554):
    # Regista o sinal para simular o encerramento repentino do servidor no momento do CTRL+\
    signal.signal(signal.SIGQUIT, ctrl_slash_handler)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
                conn.sendall(data)

if __name__ == "__main__":
    start_server()