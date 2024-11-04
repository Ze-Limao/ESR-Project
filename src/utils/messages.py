import socket
import json

class Messages:
    def encode(message: str):
        return message.encode('utf-8')
    
    def decode(message: str):
        return message.decode('utf-8')
    
    def send(conn: socket.socket, message: bytes):
        conn.send(message)
    
    def receive(conn: socket.socket):
        return conn.recv(1024)
    
    def encode_list(lst: list):
        return json.dumps(lst).encode('utf-8')
    
    def decode_list(lst: str):
        return json.loads(lst.decode('utf-8'))
      
