import json

class FileReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def check_mem_type_json(self):
        return self.file_path.endswith('.json')

    def read(self):
        try:
            with open(self.file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def read_json(self):
        if self.check_mem_type_json():
            try:
                with open(self.file_path, 'r') as file:
                    return json.load(file)
            except FileNotFoundError:
                print(f"File not found: {self.file_path}")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print(f"File {self.file_path} is not a JSON file.")
            return None