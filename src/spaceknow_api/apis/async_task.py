import logging
import threading
from apis.auth_api import AuthApi
from apis.auth_api import ApiError, ClientError, ServerError
from apis.task_api import TaskApi

logger = logging.getLogger('async_task')

class AsyncTask():
  def __init__(self, api_endpoint: str, auth_api: AuthApi, task_api: TaskApi) -> None:
      self.api_endpoint = api_endpoint
      self.client_api = auth_api
      self.task_api = task_api
      
      self.initiate_url = f"{self.api_endpoint}/search/initiate" # TODO try if it's private
      self.retreive_url = f"{self.api_endpoint}/search/retrieve"
      self.pipeline_id = None
      
      self.completed = False
      self._lock = threading.Lock()
  
  def __wait_until_ready(self, init_delay: int):
    self.task_api.wait_unit_ready(self.pipeline_id, init_delay)
    with self._lock:
      self.completed = True
  
  def initiate(self, data: dict) -> str:
    try:   
      if self.pipeline_id:
        return self.pipeline_id
      
      logger.debug("Trying to initiate new task")
      request_result = self.client_api.request(self.initiate_url, data)
      pipeline_id = request_result.get('pipelineId', None)
      init_delay = request_result.get('nextTry', 0)
      
      if not pipeline_id:
        raise ApiError("Cant't extract pipeline_id from response")
      
      logger.info(f"New task initiated with pipeline id {pipeline_id}")
      self.pipeline_id = pipeline_id
      
      check_task_thread = threading.Thread(target=self.__wait_until_ready, args=(init_delay,)) 
      check_task_thread.start()
      return self.pipeline_id
      
    except (ApiError, ClientError, ServerError) as e: 
      logger.fatal(f"Error occurred during task init phase: {e}")
      raise e
  
  def is_complete(self) -> bool:
    with self._lock:
      return self.completed
    
  def retreive(self) -> dict:
    with self._lock: 
      if (self.completed):     
        return self.client_api.request(self.retreive_url, { 'pipelineId': self.pipeline_id })
      else: 
        return {}
