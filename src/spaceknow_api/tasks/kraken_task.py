from tasks.async_task import AsyncTask
from apis.auth_api import AuthApi
from apis.task_api import TaskApi


class KrakenTask(AsyncTask):
    def __init__(self, client_api: AuthApi, task_api: TaskApi) -> None:
        super().__init__('https://api.spaceknow.com/kraken/release', client_api, task_api)
      
    def initiate_with_default(self, scene_ids: set):
        default_args = {
          'mapType': 'cars',
          'sceneIds': list(scene_ids),
          'extent': {
            'type': 'GeometryCollection',
            'geometries': [
              {
                'type': 'Polygon',
                'coordinates': [[[153.10331873088307,-27.392585786033223],[153.10634815638673,-27.387872137367758],[153.1088421008546,-27.389506793470424],[153.10691485913043,-27.39122905296285],[153.10543265183225,-27.393533000937474],[153.10331873088307,-27.392585786033223]]]
              }
            ]
          }
        }
        super().initiate(default_args)

