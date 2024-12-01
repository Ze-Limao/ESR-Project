import cv2

class VideoStream:
    def __init__(self, filename):
        self.filename = filename
        self.videoCapture = cv2.VideoCapture(filename)
        if not self.videoCapture.isOpened():
            raise IOError("Could not open video file.")
        self.frameNum = 0

    def nextFrame(self):
        """Get the next frame."""
        ret, frame = self.videoCapture.read()
        if ret:
            self.frameNum += 1
            _, encoded_frame = cv2.imencode('.jpg', frame)
            return encoded_frame.tobytes()
        else:
            self.reset()
            ret, frame = self.videoCapture.read()
            if ret:
                self.frameNum += 1
                _, encoded_frame = cv2.imencode('.jpg', frame)
                return encoded_frame.tobytes()
            else:
                return None

    def frameNbr(self):
        """Get the current frame number."""
        return self.frameNum

    def release(self):
        """Release the video capture object."""
        self.videoCapture.release()

    def reset(self):
        self.release()
        self.videoCapture = cv2.VideoCapture(self.filename)
        if not self.videoCapture.isOpened():
            raise IOError("Could not reopen video file.")