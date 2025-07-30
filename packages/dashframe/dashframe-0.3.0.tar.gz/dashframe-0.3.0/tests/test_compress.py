import os

from dashframe.compress import CompressUtils


class MyCompress(CompressUtils):
  def create_zipfile(self):
    filelist = ["Makefile", "make.bat"]
    filelist = [os.path.join("docs", myfile) for myfile in filelist]
    self.create_compress_file(filelist, os.path.join("docs", "docs.zip"))


def test_compress():
  c = MyCompress("dashframe-fake-uuid")
  c.create_zipfile()
  assert os.path.exists(os.path.join("docs", "docs.zip"))
  os.remove(os.path.join("docs", "docs.zip"))
