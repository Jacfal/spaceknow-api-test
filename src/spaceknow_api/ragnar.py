import time
import geojson 
import logging

from dataclasses import dataclass
from datetime import datetime, timedelta
from auth import SpaceKnowAuthApi

logger = logging.getLogger('ragnar')

@dataclass
class Extent: 
  type: str
  geometries: geojson.geometry

@dataclass
class RagnarApiArgs:
  cursor: str
  provider: str
  dataset: str
  startDatetime: datetime
  endDatetime: datetime
  extent: Extent
  

class SpaceKnowAsyncApi():
  def __init__(self, api_endpoint: str, client_api: SpaceKnowAuthApi) -> None:
      self.api_endpoint = api_endpoint
      self.client_api = client_api

  def initiate(self, data: dict) -> dict: 
    initiate_url = f"{self.api_endpoint}/search/initiate"
    return self.client_api.request(initiate_url, data)
    
  def retreive(self, pipeline_id: str) -> dict:
    retreive_url = f"{self.api_endpoint}/search/retrieve"
    pipeline_id_dict = { 'pipelineId': pipeline_id }
    return self.client_api.request(retreive_url, pipeline_id_dict)


class TaskingApi():
    def __init__(self, api_endpoint: str, client_api: SpaceKnowAuthApi) -> None:
      self.api_endpoint = api_endpoint
      self.client_api = client_api
      
    def get_status(self, pipeline_id: str) -> tuple:
      pipeline_id_dict = { 'pipelineId': pipeline_id }
      response = self.client_api.request(self.api_endpoint, pipeline_id_dict)
      next_try = response.get('nextTry', -1)
      status = response.get('status', 'UNKNOWN')
      return (next_try, status)

    def wait_unit_ready(self, pipeline_id: str, init_delay: int = 0, timeout_seconds: int = 60):
      logger.info(f"Waiting for completion of pipeline id {pipeline_id}, timeout: {timeout_seconds}s")
      time.sleep(init_delay)
      start_time = datetime.now()
      
      while True:    
        retreive_response = self.get_status(pipeline_id)
        next_try = retreive_response[0]
        status = retreive_response[1]
        
        logger.info(f"PipeId {pipeline_id} -> request status: {status}, next try: {next_try}")
        if status == 'RESOLVED':
          logger.info('RAGNAR done')
          break
        elif status == 'FAILED':
          logger.info('RAGNAR done with FAILED')
          break
        elif  datetime.now() > (start_time + timedelta(seconds=timeout_seconds)):
          logger.error('OPERATION TIMEOUT')
          break
        
        time.sleep(next_try)
  

class RagnarApi(SpaceKnowAsyncApi):
  def __init__(self, client_api: SpaceKnowAuthApi) -> None:
      super().__init__('https://api.spaceknow.com/imagery', client_api)
