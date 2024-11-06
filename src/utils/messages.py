import socket
import json

class Messages_UDP:
    def encode(message: str):
        return message.encode('utf-8')
    
    def decode(message: str):
        return message.decode('utf-8')
    
    def send_and_receive(conn: socket.socket, message: bytes, ip: str, port: int, timeout: float = 2.0, retries: int = 3):
        conn.sendto(message, (ip, port))
        conn.settimeout(timeout)
        for _ in range(retries):
            try:
                data, _ = conn.recvfrom(1024)
                return data
            except socket.timeout:
                conn.sendto(message, (ip, port))
        return None
    
    def encode_list(lst: list):
        return json.dumps(lst).encode('utf-8')
    
    def decode_list(lst: str):
        return json.loads(lst.decode('utf-8'))
      
