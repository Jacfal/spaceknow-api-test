from tasks.async_task import AsyncTask
from apis.auth_api import AuthApi
from apis.task_api import TaskApi


class KrakenTask(AsyncTask):
    def __init__(self, client_api: AuthApi, task_api: TaskApi) -> None:
        super().__init__('https://api.spaceknow.com/kraken/release', client_api, task_api)
      
    def initiate_with_default(self, scene_ids: set, extent) -> str:
        default_args = {
          'mapType': 'cars',
          'sceneIds': list(scene_ids),
          'extent': extent
        }
        return super().initiate(default_args)

