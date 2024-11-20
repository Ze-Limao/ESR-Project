import socket, threading
import time
from ..utils.stream.VideoStream import VideoStream
from ..utils.stream.RtpPacket import RtpPacket
from ..utils.safestring import SafeString

class ServerStream:
    def __init__(self, videoPath: str, streamPort: int):
        self.oNodeIp: SafeString = SafeString()
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp_socket.bind(('', streamPort))
        self.streamPort = streamPort

        self.videoStream = VideoStream(videoPath)
        self.stop_event = threading.Event()

    def set_oNodeIp(self, oNodeIp: str) -> None:
        self.oNodeIp.write(oNodeIp)

    def send_streaming(self) -> None:
        while not self.stop_event.is_set():
            data = self.videoStream.nextFrame()
            if data:
                frameNumber = self.videoStream.frameNbr()
                try:
                    print(f"Sending frame {frameNumber}")
                    print(f"Ip: {self.oNodeIp.read()}")
                    self.rtp_socket.sendto(self.makeRtp(data, frameNumber), (self.oNodeIp.read(), self.streamPort))
                except:
                    pass
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

    def close(self) -> None:
        self.stop_event.set()
        self.rtp_socket.close()