import socket, threading, sys
from .ServerStream import ServerStream
from ..utils.config import POINTS_OF_PRESENCE, ONODE_PORT, VIDEO_FILES, OCLIENT_PORT
from ..utils.messages import Messages_UDP

class Server:	
	def __init__(self):
		self.socket_clients = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_clients.bind(('', OCLIENT_PORT))

		self.socket_oNodes = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_oNodes.bind(('', ONODE_PORT))

		self.streams = {video: ServerStream(video, port) for video, port in VIDEO_FILES.items()}

	def accept_clients(self) -> None:
		while True:
			_, addr = self.socket_clients.recvfrom(1024)
			print(f"Received connection from {addr}")
			Messages_UDP.send(self.socket_clients, Messages_UDP.encode_json(POINTS_OF_PRESENCE), addr[0], addr[1])

	def receive_resquest_streaming(self) -> None:
		while True:
			data, addr = self.socket_oNodes.recvfrom(1024)
			video = Messages_UDP.decode(data)
			print(f"Received request for streaming {video} from {addr}")
			if video in self.streams:
				Messages_UDP.send(self.socket_oNodes,b'', addr[0], addr[1])
				print("Setted onode ip")
				self.streams[video].set_oNodeIp(addr[0])
				print("Setted onode ip")
				print(self.streams[video].oNodeIp)

	def send_streaming(self) -> None:
		for serverstream in self.streams.values():
			threading.Thread(target=serverstream.send_streaming).start()

	def main(self) -> None:
		print("Server is listening on port", ONODE_PORT)
		threading.Thread(target=self.send_streaming).start()
		threading.Thread(target=self.accept_clients).start()
		threading.Thread(target=self.receive_resquest_streaming).start()

if __name__ == "__main__":
	if len(sys.argv) != 1:
		print("python3 -m src.server.Server")
		sys.exit(1)
	(Server()).main()
