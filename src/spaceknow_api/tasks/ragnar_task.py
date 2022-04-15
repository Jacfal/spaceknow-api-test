from array import array
from tasks.async_task import AsyncTask
from apis.auth_api import AuthApi
from apis.task_api import TaskApi


class RagnarTask(AsyncTask):
    def __init__(self, client_api: AuthApi, task_api: TaskApi) -> None:
        super().__init__('https://api.spaceknow.com/imagery/search', client_api, task_api)

    def retreive_scene_ids(self) -> set:
        retrieve_results = super().retreive().get('results', [])
        return set(filter(lambda i: i, map(lambda j: j.get('sceneId', None), retrieve_results)))   
