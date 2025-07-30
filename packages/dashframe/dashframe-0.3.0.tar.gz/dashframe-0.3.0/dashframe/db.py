"""Management of task-id and uuid"""

import os
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class TaskMapping(Base):
  __tablename__ = "task_mappings"

  task_id = Column(String(36), primary_key=True)
  uuid = Column(String(36), nullable=False, index=True)
  created_at = Column(DateTime, default=datetime.utcnow)

  def __repr__(self):
    return f"<TaskMapping(task_id='{self.task_id}', uuid='{self.uuid}')>"


# 数据库连接配置
DATABASE_URL = "sqlite:///tasks.db"  # 使用 SQLite 作为示例，你可以根据需要修改为其他数据库

# 创建数据库引擎，添加 connect_args 来支持多线程
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# 如果文件不存在，或者表不存在，创建所有表
def init_db():
  if not os.path.exists("tasks.db"):
    print("create db")
    Base.metadata.create_all(engine)
    print("create db success")
  else:
    print("db already exists")


# 创建线程安全的会话工厂
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


@contextmanager
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


def get_task_mapping(task_id: str):
  with get_db() as db:
    return db.query(TaskMapping).filter(TaskMapping.task_id == task_id).first()


def create_task_mapping(task_id: str, uuid: str):
  with get_db() as db:
    db.add(TaskMapping(task_id=task_id, uuid=uuid))
    db.commit()


if __name__ == "__main__":
  init_db()
