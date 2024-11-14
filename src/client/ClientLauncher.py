import sys
from tkinter import Tk
from .Client import Client
from typing import TypedDict, List
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, STREAM_PORT, RTP_PORT
import socket
import time

class PointsOfPresence(TypedDict):
	ip_adress: str
	velocity: int

class ClientLauncher:
	def __init__(self, serverAddr: str, fileName: str):
		self.serverAddr = serverAddr
		self.serverPort = STREAM_PORT
		self.rtpPort = RTP_PORT
		self.fileName = fileName
		self.root = Tk()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.socket.bind(('', ONODE_PORT))
		self.points_of_presence: List[PointsOfPresence] = []
		
	def create_client(self):
		app = Client(self.root, self.serverAddr, self.serverPort, self.rtpPort, self.fileName)
		app.master.title("RTPClient")	
		self.root.mainloop()
		
	def ask_points_presence(self):
		points_of_presence_enconded = Messages_UDP.send_and_receive(self.socket, b'' ,self.serverAddr, ONODE_PORT)
		if points_of_presence_enconded is None:
			print("Error: Could not get points of presence")
			sys.exit(1)
		points_of_presence = Messages_UDP.decode_json(points_of_presence_enconded)
		self.set_points_presence(points_of_presence)
		print(self.points_of_presence)
		
	def set_points_presence(self, points_of_presence: list):
		for point in points_of_presence:
			self.points_of_presence.append(
				PointsOfPresence(
					ip_adress=point,
					velocity=1
				)
			)

	def check_status_points_presence(self):
		for point in self.points_of_presence:
			timestamp = time.time()
			response = Messages_UDP.send_and_receive(self.socket, b'', point['ip_adress'], ONODE_PORT)
			if response is None:
				print(f"Error: Could not get response from point of presence {point['ip_adress']}")
				point['velocity'] = float('inf')
			else:
				point['velocity'] = time.time() - timestamp
				print(f"Point of presence {point['ip_adress']} has latency {point['velocity']}")

if __name__ == "__main__":
	try:
		serverAddr = sys.argv[1]
		fileName = sys.argv[2]
	except:
		print("[Usage: ClientLauncher.py Server_name Video_file]\n")

	client_launcher = ClientLauncher(serverAddr, fileName)
	client_launcher.ask_points_presence()
	client_launcher.check_status_points_presence()
	client_launcher.create_client()