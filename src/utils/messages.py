import socket
import json
from typing import Union

class Messages_UDP:
    def send_and_receive(conn: socket.socket, message: bytes, ip: str, port: int, timeout: float = 2.0, retries: int = 3) -> bytes:
        conn.sendto(message, (ip, port))
        conn.settimeout(timeout)
        for _ in range(retries):
            try:
                data, _ = conn.recvfrom(1024)
                return data
            except socket.timeout:
                conn.sendto(message, (ip, port))
        return None
    
    def send(conn: socket.socket, message: bytes, ip: str, port: int) -> None:
        conn.sendto(message, (ip, port))

    def encode_json(lst: Union[list, dict]) -> bytes:
        return json.dumps(lst).encode('utf-8')

    def decode_json(lst: bytes) -> Union[list, dict]:
        return json.loads(lst.decode('utf-8'))
      
