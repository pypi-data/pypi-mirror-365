import os
import uuid
from datetime import datetime
from typing import Any

from dashframe.log import Log


def get_folder(uuid: str):
  folder = f"./data/{uuid}"
  if not os.path.exists(folder):
    os.makedirs(folder)

  def fn(filename: str):
    return f"{folder}/{filename}"

  return fn


class RunError(Exception):
  """执行程序异常时，抛出此异常"""

  pass


class Runner(object):
  """
  Runner is a class that can be used to execute the program/algorithm/model.
  """

  def __init__(self, uuid: str = ""):
    if uuid == "":
      self.uuid = self._generate_compute_id()
    else:
      self.uuid = uuid
    self.get_path = get_folder(self.uuid)

  def _generate_compute_id(self):
    uuid_str = str(uuid.uuid4())
    return uuid_str

  def get_logger(self):
    return Log(self.get_path("log.txt"))

  def compute(self, input_data: Any):
    """
    计算逻辑
    """
    raise NotImplementedError("子类必须实现此方法")

  def is_fake(self):
    return False

  def fake_fn(self):
    import time

    time.sleep(2)

  def run(self, input_data: Any):
    if self.is_fake():
      self.fake_fn()
      return

    # append to main.log
    try:
      with open("./data/main.log", "a") as f:
        f.write(f"{datetime.now()} run {self.uuid}\n")
      self.compute(input_data)
      with open("./data/main.log", "a") as f:
        f.write(f"{datetime.now()} end {self.uuid}\n")
    except Exception as e:
      with open("./data/main.log", "a") as f:
        f.write(f"{datetime.now()} error {self.uuid} {e}\n")
      raise RunError("执行程序异常")
