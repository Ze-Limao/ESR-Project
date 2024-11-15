import threading

# SafeString: class that implements a thread-safe string. Implements most of the methods of a string with a lock
class SafeString:
    def __init__(self):
        self.lock = threading.Lock()
        self.string = None

    def write(self, value):
        with self.lock:
            self.string = value

    def read(self):
        with self.lock:
            return self.string