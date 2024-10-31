from ...utils.filereader import FileReader
from .topology import Topology

class Bootstrap:
    def __init__(self, file_path):
        self.file_path = file_path
        self.topology = Topology()
        self.read_file()

    def read_file(self):
        file_reader = FileReader(self.file_path)
        file_contents = file_reader.read()
        self.parse_contents(file_contents)

    def parse_contents(self, contents):
        lines = contents.split('\n')
        #TODO: Implement parsing logic

    def get_topology(self):
        return self.topology