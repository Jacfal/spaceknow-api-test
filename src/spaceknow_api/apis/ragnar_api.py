from apis.async_api import AsyncApi
from apis.auth_api import AuthApi


class RagnarApi(AsyncApi):
  def __init__(self, client_api: AuthApi) -> None:
      super().__init__('https://api.spaceknow.com/imagery', client_api)
