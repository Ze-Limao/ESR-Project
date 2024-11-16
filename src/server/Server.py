import sys, socket
import threading
from .ServerStream import ServerStream
from ..utils.config import POINTS_OF_PRESENCE, ONODE_PORT
from ..utils.messages import Messages_UDP

class Server:	
	def __init__(self):
		self.socket_clients = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_clients.bind(('', ONODE_PORT))

	def accept_clients(self) -> None:
		_, addr = self.socket_clients.recvfrom(1024)
		print(f"Received connection from {addr}")
		Messages_UDP.send(self.socket_clients, Messages_UDP.encode_json(POINTS_OF_PRESENCE), addr[0], addr[1])

	def send_streaming(self) -> None:
		ServerStream().send_streaming()

	def main(self) -> None:
		print("Server is listening on port", ONODE_PORT)
		threading.Thread(target=self.send_streaming).start()
		while True:
			self.accept_clients()

if __name__ == "__main__":
	(Server()).main()
