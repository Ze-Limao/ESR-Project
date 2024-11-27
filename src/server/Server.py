import socket, threading, sys, signal
from .ServerStream import ServerStream
from ..utils.config import POINTS_OF_PRESENCE, ONODE_PORT, VIDEO_FILES, OCLIENT_PORT
from ..utils.messages import Messages_UDP
from typing import List

class Server:	
	def __init__(self):
		self.socket_clients = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_clients.bind(('', OCLIENT_PORT))

		self.socket_oNodes = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_oNodes.bind(('', ONODE_PORT))

		self.streams = {video: ServerStream(video, port) for video, port in VIDEO_FILES.items()}

		self.threads : List[threading.Thread] = []
		self.stop_event = threading.Event()

	def accept_clients(self) -> None:
		self.socket_clients.settimeout(1)  # Set a timeout of 1 second
		while not self.stop_event.is_set():
			try:
				_, addr = self.socket_clients.recvfrom(1024)
				print(f"Received connection from {addr}")
				Messages_UDP.send(
					self.socket_clients,
					Messages_UDP.encode_json(POINTS_OF_PRESENCE),
					addr[0],
					addr[1]
				)
			except socket.timeout:
				# Timeout occurred, loop back and check stop_event
				continue
			except Exception as e:
				print(f"An error occurred: {e}")
				break

	def receive_resquest_streaming(self) -> None:
		self.socket_oNodes.settimeout(1)  # Set a 1-second timeout
		while not self.stop_event.is_set():
			try:
				data, addr = self.socket_oNodes.recvfrom(1024)
				video = Messages_UDP.decode_json(data)["stream"]
				print(f"Received request for streaming {video} from {addr}")
				if video in self.streams:
					Messages_UDP.send(self.socket_oNodes, b'', addr[0], addr[1])
					self.streams[video].set_oNodeIp(addr[0])
			except socket.timeout:
				# Timeout occurred, loop back and check stop_event
				continue
			except Exception as e:
				print(f"An error occurred: {e}")
				break

	def set_threads(self) -> None:
		print("Server is listening on port", ONODE_PORT)
		
		for serverstream in self.streams.values():
			self.threads.append(threading.Thread(target=serverstream.send_streaming))

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

if __name__ == "__main__":
	if len(sys.argv) != 1:
		print("python3 -m src.server.Server")
		sys.exit(1)
	
	# Register the signal to shut down the server at the time of CTRL+C
	signal.signal(signal.SIGINT, ctrlc_handler)

	server = Server()
	server.set_threads()
