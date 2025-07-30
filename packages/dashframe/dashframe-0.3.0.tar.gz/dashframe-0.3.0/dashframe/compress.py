"""create compress file"""

import os
import zipfile

from dashframe.runner import get_folder


class CompressUtils(object):
  """Compress result."""

  def __init__(self, uuid: str):
    self.uuid = uuid

  def get_folder(self):
    """return folder path"""
    return get_folder(self.uuid)(filename="")

  def create_compress_file(self, file_path: list[str], compress_file_path: str):
    with zipfile.ZipFile(compress_file_path, "w") as zip_file:
      for file in file_path:
        zip_file.write(file, os.path.basename(file))
