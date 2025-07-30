from dashframe import db


class BaseManager(object):
  def create_mapping(self, task_id, uuid):
    return db.create_task_mapping(task_id, uuid)

  def get_uuid_by_task_id(self, task_id):
    task_mapping = db.get_task_mapping(task_id)
    if task_mapping is None:
      raise ValueError(f"map不存在, task_id: {task_id}")
    return task_mapping.uuid

  def is_done(self, task_id):
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=self.get_celery_app())
    return result.ready()

  def get_celery_app(self):
    raise NotImplementedError("You must implement this method")
