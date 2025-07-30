import os
import pathlib


class Log:
  def __init__(self, file_path: str):
    self.file_path = file_path
    pathlib.Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

  def print(self, message: str):
    print(message)
    with self.open_file() as f:
      f.write(str(message) + "\n")

  def open_file(self):
    return open(self.file_path, "a")

  def get(self):
    """get total log content"""
    if not os.path.exists(self.file_path):
      return "no log."

    with open(self.file_path, "r") as f:
      return f.read()

  def get_file(self):
    """for tqdm write."""
    return self.open_file()
