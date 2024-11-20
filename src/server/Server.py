import socket, threading, sys, signal
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

		self.threads = []
		self.stop_event = threading.Event()

	def accept_clients(self) -> None:
		while not self.stop_event.is_set():
			_, addr = self.socket_clients.recvfrom(1024)
			print(f"Received connection from {addr}")
			Messages_UDP.send(self.socket_clients, Messages_UDP.encode_json(POINTS_OF_PRESENCE), addr[0], addr[1])

	def receive_resquest_streaming(self) -> None:
		while not self.stop_event.is_set():
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
			thread = threading.Thread(target=serverstream.send_streaming)
			self.threads.append(thread)
			thread.start()

	def set_threads(self) -> None:
		print("Server is listening on port", ONODE_PORT)
		self.threads.append(threading.Thread(target=self.send_streaming))
		self.threads.append(threading.Thread(target=self.accept_clients))
		self.threads.append(threading.Thread(target=self.receive_resquest_streaming))
		for thread in self.threads:
			thread.start()
		
	def closeStreaming(self) -> None:
		# Close Threads
		self.stop_event.set()
		for serverstream in self.streams.values():
			serverstream.close()
		for thread in self.threads:
			thread.join()
		# Close sockets
		self.socket_clients.close()
		self.socket_oNodes.close()

def ctrlc_handler(sig, frame):
    print("Closing the server and the threads...")
    server.closeStreaming()
    sys.exit(0)	

if __name__ == "__main__":
	if len(sys.argv) != 1:
		print("python3 -m src.server.Server")
		sys.exit(1)
	
	# Register the signal to shut down the server at the time of CTRL+C
	signal.signal(signal.SIGINT, ctrlc_handler)

	server = Server()
	server.set_threads()
