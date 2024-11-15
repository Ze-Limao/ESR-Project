import sys, socket
import threading
from .ServerWorker import ServerWorker
from ..utils.config import STREAM_PORT, POINTS_OF_PRESENCE, ONODE_PORT
from ..utils.messages import Messages_UDP

class Server:	
	def __init__(self):
		self.socket_clients = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_clients.bind(('', ONODE_PORT))

		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.rtspSocket.bind(('', STREAM_PORT))
		self.rtspSocket.listen(5) 

	def accept_clients(self) -> None:
		_, addr = self.socket_clients.recvfrom(1024)
		print(f"Received connection from {addr}")
		Messages_UDP.send(self.socket_clients, Messages_UDP.encode_json(POINTS_OF_PRESENCE), addr[0], addr[1])

	def accept_streaming(self) -> None:
		while True:
			clientInfo = {}
			clientInfo['rtspSocket'] = self.rtspSocket.accept()
			ServerWorker(clientInfo).run()

	def main(self) -> None:
		print("Server is listening on port", ONODE_PORT)
		threading.Thread(target=self.accept_streaming).start()
		while True:
			self.accept_clients()

if __name__ == "__main__":
	(Server()).main()
