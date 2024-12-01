import sys, threading, time, socket, signal
from tkinter import Tk
from .ClientStream import ClientStream
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, SERVER_IP, OCLIENT_PORT, ASK_FOR_STREAM_PORT, OCLIENT_PORT_MONITORING
from ..utils.safemap import SafeMap
from ..utils.safestring import SafeString
from typing import List

class oClient:
	def __init__(self, fileName: str):
		self.serverAddr: str = SERVER_IP
		self.fileName: str = fileName
		self.root = Tk()
		# SOCKET TO ASK FOR STREAMING
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.socket.bind(('', ONODE_PORT))

		# SOCKET TO ASK SERVER FOR POINTS OF PRESENCE
		self.socket_oClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_oClient.bind(('', OCLIENT_PORT))

		self.port = OCLIENT_PORT_MONITORING

		self.points_of_presence = SafeMap()
		self.sockets_pp = {}
		self.point_of_presence = SafeString()

		self.threads : List[threading.Thread] = []
		self.stop_event = threading.Event()
		self.client = None

	def ask_for_streaming(self) -> None:
		data = Messages_UDP.send_and_receive(self.socket, Messages_UDP.encode_json({"stream": self.fileName}), self.point_of_presence.read(), ASK_FOR_STREAM_PORT)
		if data is None:
			print("Error: Could not get response from point of presence")
			sys.exit(1)

	def create_client(self) -> None:
		self.client = ClientStream(self.root, self.fileName)
		self.root.mainloop()
		
	def ask_points_presence(self) -> None:
		points_of_presence_enconded = Messages_UDP.send_and_receive(self.socket_oClient, b'' ,self.serverAddr, OCLIENT_PORT)
		if points_of_presence_enconded is None:
			print("Error: Could not get points of presence")
			sys.exit(1)
		points_of_presence = Messages_UDP.decode_json(points_of_presence_enconded)
		self.set_points_presence(points_of_presence)
		self.socket_oClient.close()
		
	def set_points_presence(self, points_of_presence: list):
		for point in points_of_presence:
			socket_pp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			socket_pp.bind(('', self.port))
			self.port += 1
			self.points_of_presence.put(point, float('inf'))
			self.sockets_pp[point] = socket_pp

	def update_point_of_presence_status(self, point: str) -> None:
		timestamp = time.time()
		socket_pp: socket.socket = self.sockets_pp[point]
		response = Messages_UDP.send_and_receive(socket_pp, b'', point, ONODE_PORT)
		if response is None:
			print(f"Error: Could not get response from point of presence {point}")
			self.points_of_presence.put(point, float('inf'))
		else:
			delay = time.time() - timestamp
			self.points_of_presence.put(point, delay)
			print(f"Point of presence {point} has latency {delay}")
			current_point = self.point_of_presence.read()
			if current_point == None:
				self.point_of_presence.write(point)
			else:
				if self.points_of_presence.get(current_point) > delay:
					self.point_of_presence.write(point)

	def first_check_status_points_presence(self) -> None:
		threads = []
		for point in self.points_of_presence.get_keys():
			threads.append(threading.Thread(target=self.update_point_of_presence_status, args=(point,)))
		
		for thread in threads:
			thread.start()
		
		for thread in threads:
			thread.join()

		if self.point_of_presence.read() == None:
			print("Error: Could not find a point of presence")
			sys.exit(1)

	def start_thread(self, point: str) -> None:
		while not self.stop_event.is_set():
			self.update_point_of_presence_status(point)
			time.sleep(5)

	def check_status_points_presence(self) -> None:
		for point in self.points_of_presence.get_keys():
			thread = threading.Thread(target=self.start_thread, args=(point,))
			thread.start()
			self.threads.append(thread)

	def closeStreaming(self) -> None:
		# Close Threads
		self.stop_event.set()
		self.client.closeStream()
		for thread in self.threads:
			thread.join()
		
		for socket_pp in self.sockets_pp.values():
			socket_pp.close()
		# Close sockets
		self.socket.close()
		self.socket_oClient.close()

def ctrlc_handler(sig, frame):
    print("Closing the server and the threads...")
    oclient.closeStreaming()
	
if __name__ == "__main__":
	try:
		fileName = sys.argv[1]
	except:
		print("[Usage: python3 -m src.client.oClient <video_file_path>]\n")

	# Register the signal to shut down the server at the time of CTRL+C
	signal.signal(signal.SIGINT, ctrlc_handler)

	oclient = oClient(fileName)
	oclient.ask_points_presence()
	oclient.first_check_status_points_presence()
	oclient.ask_for_streaming()
	oclient.check_status_points_presence()
	oclient.create_client()