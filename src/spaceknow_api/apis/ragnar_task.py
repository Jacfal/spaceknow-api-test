from apis.async_api import AsyncTask
from apis.auth_api import AuthApi
from apis.task_api import TaskApi


class RagnarTask(AsyncTask):
  def __init__(self, client_api: AuthApi, task_api: TaskApi) -> None:
      super().__init__('https://api.spaceknow.com/imagery', client_api, task_api)
