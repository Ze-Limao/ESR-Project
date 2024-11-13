import sys
from tkinter import Tk
from .Client import Client
from typing import TypedDict, List
from ..utils.messages import Messages_UDP
from ..utils.config import SERVER_PORT
import socket

class PointsOfPresence(TypedDict):
	ip_adress: str
	velocity: int

class ClientLauncher:
	def __init__(self, serverAddr: str, serverPort: int, rtpPort: int, fileName: str):
		self.serverAddr = serverAddr
		self.serverPort = serverPort
		self.rtpPort = rtpPort
		self.fileName = fileName
		self.root = Tk()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.socket.bind(('', SERVER_PORT))
		self.points_of_presence: List[PointsOfPresence] = []
		
	def create_client(self):
		app = Client(self.root, self.serverAddr, self.serverPort, self.rtpPort, self.fileName)
		app.master.title("RTPClient")	
		self.root.mainloop()
		
	def ask_points_presence(self):
		points_of_presence_enconded = Messages_UDP.send_and_receive(self.socket, b'' ,self.serverAddr, SERVER_PORT)
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

if __name__ == "__main__":
	try:
		serverAddr = sys.argv[1]
		serverPort = sys.argv[2]
		rtpPort = sys.argv[3]
		fileName = sys.argv[4]
	except:
		print("[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n")

	client_launcher = ClientLauncher(serverAddr, int(serverPort), rtpPort, fileName)
	client_launcher.ask_points_presence()
	client_launcher.check_status_points_presence()
	client_launcher.create_client()