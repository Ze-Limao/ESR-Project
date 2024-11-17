import sys, threading, time, socket
from tkinter import Tk
from .ClientStream import ClientStream
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, RTP_PORT, SERVER_IP, OCLIENT_PORT
from ..utils.safemap import SafeMap
from ..utils.safestring import SafeString

class oClient:
	def __init__(self, fileName: str):
		self.serverAddr: str = SERVER_IP
		self.rtpPort: int = RTP_PORT
		self.fileName: str = fileName
		self.root = Tk()
		# SOCKET TO ASK FOR STREAMING
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.socket.bind(('', ONODE_PORT))

		# SOCKET TO ASK SERVER FOR POINTS OF PRESENCE
		self.socket_oClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_oClient.bind(('', OCLIENT_PORT))

		self.points_of_presence = SafeMap()
		self.point_of_presence = SafeString()

	def ask_for_streaming(self) -> None:
		data = Messages_UDP.send_and_receive(self.socket, Messages_UDP.encode(self.fileName), self.point_of_presence.read(), ONODE_PORT)
		if data is None:
			print("Error: Could not get response from point of presence")
			sys.exit(1)

	def create_client(self) -> None:
		ClientStream(self.root, self.fileName)
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
			self.points_of_presence.put(point, float('inf'))

	def check_status_point_of_presence(self, point: str) -> None:
		timestamp = time.time()
		response = Messages_UDP.send_and_receive(self.socket, b'', point, ONODE_PORT)
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
			threads.append(threading.Thread(target=self.check_status_point_of_presence, args=(point,)))
		
		for thread in threads:
			thread.start()
		
		for thread in threads:
			thread.join()

		if self.point_of_presence.read() == None:
			print("Error: Could not find a point of presence")
			sys.exit(1)

	def check_status_points_presence(self) -> None:
		while True:
			time.sleep(5)
			for point in self.points_of_presence.get_keys():
				threading.Thread(target=self.check_status_point_of_presence, args=(point,)).start()
			
if __name__ == "__main__":
	try:
		fileName = sys.argv[1]
	except:
		print("[Usage: ClientLauncher.py Video_file]\n")

	oclient = oClient(fileName)
	oclient.ask_points_presence()
	oclient.first_check_status_points_presence()
	oclient.ask_for_streaming()
	threading.Thread(target=oclient.check_status_points_presence).start()
	oclient.create_client()