import socket, threading
from tkinter import *
from PIL import Image, ImageTk
from ..utils.config import RTP_PORT, SERVER_IP, VIDEO_FILES
from ..utils.stream.RtpPacket import RtpPacket
import time

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"


class ClientStream:
    def __init__(self, master: Tk, fileName: str):
        self.serverAddr: str = SERVER_IP
        self.serverPort: int = VIDEO_FILES[fileName]
        self.rtpPort: int = RTP_PORT
        self.fileName: str = fileName
        self.master: Tk = master
        self.master.title("RTPClient")
        self.frameNbr = 0
        self.timestamp= str(int(time.time() * 1000))
        
        self.rtpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtpsocket.bind(('', self.serverPort))

        self.event = threading.Event()
        self.thread = threading.Thread(target=self.receiveRtp)

        self.createWidgets()
    
    def createWidgets(self):
        """Build GUI."""
        self.playButton = Button(self.master, width=20, padx=3, pady=3)
        self.playButton["text"] = "Play"
        self.playButton["command"] = self.playStream
        self.playButton.grid(row=1, column=0, padx=2, pady=2)

        self.closeButton = Button(self.master, width=20, padx=3, pady=3)
        self.closeButton["text"] = "Close"
        self.closeButton["command"] = self.closeStream
        self.closeButton.grid(row=1, column=1, padx=2, pady=2)

        self.label: Label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=2, sticky=W+E+N+S, padx=5, pady=5)

    def playStream(self):
        self.thread.start()

    def closeStream(self):
        self.master.destroy()
        self.rtpsocket.close()
        self.event.set()
        self.thread.join()
    
    def receiveRtp(self):
        while not self.event.is_set():
            data = self.rtpsocket.recv(20480)
            if data:
                rtpPacket = RtpPacket()
                rtpPacket.decode(data)

                currFrameNbr = rtpPacket.seqNum()
                print("Current Seq Num: " + str(currFrameNbr))
                                    
                if currFrameNbr > self.frameNbr: # Discard the late packet
                    self.frameNbr = currFrameNbr
                    self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
    
    def updateMovie(self, imageFile):
        image = Image.open(imageFile)
        photo = ImageTk.PhotoImage(image)
        
        # Dynamically set the label size to match the image
        self.label.configure(image=photo, height=image.size[1], width=image.size[0]) 
        self.label.image = photo

    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + self.timestamp + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()
              
        return cachename