import socket
import time
from ..utils.config import STREAM_PORT
from ..utils.stream.VideoStream import VideoStream
from ..utils.stream.RtpPacket import RtpPacket

class ServerStream:
    def __init__(self, oNodeIp: str= None, videoPath: str= "videos/video_BrskEdu.mp4"):
        self.oNodeIp: str = oNodeIp
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp_socket.bind(('', STREAM_PORT))

        self.videoStream = VideoStream(videoPath)

    def set_oNodeIp(self, oNodeIp: str) -> None:
        self.oNodeIp = oNodeIp

    def send_streaming(self) -> None:
        while True:
            data = self.videoStream.nextFrame()
            if data:
                frameNumber = self.videoStream.frameNbr()
                try:
                    self.rtp_socket.sendto(self.makeRtp(data, frameNumber), (self.oNodeIp, STREAM_PORT))
                except:
                    print("Connection Error")
            time.sleep(0.05)
    
    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26 # MJPEG type
        seqnum = frameNbr
        ssrc = 0 
        
        rtpPacket = RtpPacket()
        
        rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
        
        return rtpPacket.getPacket()