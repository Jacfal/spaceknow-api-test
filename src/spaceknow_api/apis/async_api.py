from apis.auth_api import AuthApi


class AsyncApi():
  def __init__(self, api_endpoint: str, client_api: AuthApi) -> None:
      self.api_endpoint = api_endpoint
      self.client_api = client_api

  def initiate(self, data: dict) -> dict: 
    initiate_url = f"{self.api_endpoint}/search/initiate"
    return self.client_api.request(initiate_url, data)
    
  def retreive(self, pipeline_id: str) -> dict:
    retreive_url = f"{self.api_endpoint}/search/retrieve"
    pipeline_id_dict = { 'pipelineId': pipeline_id }
    return self.client_api.request(retreive_url, pipeline_id_dict)
