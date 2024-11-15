import sys
from tkinter import Tk
from .Client import Client
from typing import TypedDict, Dict
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, STREAM_PORT, RTP_PORT, SERVER_IP
import socket
import time

class ClientLauncher:
	def __init__(self, fileName: str):
		self.serverAddr: str = SERVER_IP
		self.serverPort: int = STREAM_PORT
		self.rtpPort: int = RTP_PORT
		self.fileName: str = fileName
		self.root = Tk()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.socket.bind(('', ONODE_PORT))
		self.points_of_presence: Dict[str, float] = {}
		self.point_of_presence: str = None
		
	def create_client(self) -> None:
		app = Client(self.root, self.serverAddr, self.serverPort, self.rtpPort, self.fileName)
		app.master.title("RTPClient")	
		self.root.mainloop()
		
	def ask_points_presence(self) -> None:
		points_of_presence_enconded = Messages_UDP.send_and_receive(self.socket, b'' ,self.serverAddr, ONODE_PORT)
		if points_of_presence_enconded is None:
			print("Error: Could not get points of presence")
			sys.exit(1)
		points_of_presence = Messages_UDP.decode_json(points_of_presence_enconded)
		self.set_points_presence(points_of_presence)
		print(self.points_of_presence)
		
	def set_points_presence(self, points_of_presence: list):
		for point in points_of_presence:
			self.points_of_presence[point] = float('inf') 

	def check_status_points_presence(self) -> None:
		for point in self.points_of_presence.keys():
			timestamp = time.time()
			response = Messages_UDP.send_and_receive(self.socket, b'', point, ONODE_PORT)
			if response is None:
				print(f"Error: Could not get response from point of presence {point}")
				self.points_of_presence[point] = float('inf')
			else:
				self.points_of_presence[point] = time.time() - timestamp
				print(f"Point of presence {point} has latency {self.points_of_presence[point]}")
				if self.point_of_presence == None:
					self.point_of_presence = point
				else:
					if self.points_of_presence[self.point_of_presence] > self.points_of_presence[point]:
						self.point_of_presence = point
		print(f"Point of presence selected: {self.point_of_presence}")
		print(self.points_of_presence)

if __name__ == "__main__":
	try:
		fileName = sys.argv[1]
	except:
		print("[Usage: ClientLauncher.py Video_file]\n")

	client_launcher = ClientLauncher(fileName)
	client_launcher.ask_points_presence()
	client_launcher.check_status_points_presence()
	client_launcher.create_client()