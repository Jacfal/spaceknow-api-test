import json
import logging
import requests
from os.path import exists


jwt_storage_default_path = '/tmp/space_know_token'
logger = logging.getLogger('api_logger')

class CLientError(Exception):
  pass

class ServerError(Exception):
  pass

class AuthApi():
  def __init__(self, auth_endpoint: str, username: str, password: str):
    self.auth_endpoint = auth_endpoint
    self.username = username
    self.password = password
    self.auth_token = None

  def __authorize(self, headers: dict, force: bool = False) -> dict: 
    logger.debug("Trying to authorized request")
    id_token = None
    
    if exists(jwt_storage_default_path) and not force: 
      # load token from local 
      logger.debug(f"Loading token from local {jwt_storage_default_path}")
     
      try: 
        with open(jwt_storage_default_path, 'r') as f:
          auth_response = json.loads(f.read())
          id_token = auth_response['id_token']
      except Exception as e: 
        logger.error(f"Can't read token from local storage {jwt_storage_default_path}: {str(e)}")
        self.__authorize(headers, force=True)
        
    else:
      # request token
      logger.debug(f"Requesting token from auth endpoint {self.auth_endpoint}")
      auth_response = self.__request_JWT()
      
      # save token to local
      with open(jwt_storage_default_path, 'w') as f:
        f.write(json.dumps(auth_response)) # TODO base64
        
      id_token = auth_response['id_token'] 
        
    headers['Authorization'] = f"Bearer {id_token}"
    
  def __request_JWT(self) -> json:
    request_body = {
      "client_id": "hmWJcfhRouDOaJK2L8asREMlMrv3jFE1",
      "username": self.username,
      "password": self.password,
      "connection": "Username-Password-Authentication",
      "grant_type": "password",
      "scope": "openid"
    }
    
    response = requests.post(self.auth_endpoint, json=request_body)
    logger.debug(f"Auth response status code {response.status_code}")
    
    if response.status_code == 200: 
      logger.debug("Token request successfull from auth endpoint {self.auth_endpoint}")
      return response.json()
    else:
      logger.error(f"Can't get auth token from auth endpoint {self.auth_endpoint}")
      pass # TODO    
    
  def request(self, api_url: str, data: dict) -> json:     
    request_headers = {
      'Host': 'api.spaceknow.com' # TODO 
    }
    
    self.__authorize(request_headers)
    print(data)
    response = requests.post(api_url, headers=request_headers, json=data)
    
    response_ready_log = f"Api request complete with status code: {response.status_code}"
    logger.info(response_ready_log)
    
    if response.status_code >= 200 and response.status_code <= 299:
      # OK
      return response.json()
    elif response.status_code >= 400 and response.status_code <= 499:
      # client side err
      err_msg = response.json().get('errorMessage', None)
      
      if (err_msg and "Signature has expired" in err_msg):
        # expired JWT token, ask for the new one
        logger.info('JWT token has expired, asking for the new one')
        self.__authorize(headers={}, force=True) # just dummy call for token recreation
        return self.request(api_url, data) 
      else:
        err_msg = f"Client side error occurs: {response.text}"
        logger.error(err_msg)
        raise CLientError(err_msg)
    elif response.status_code >= 500 and response.status_code <= 599:
      # server side err
      err_msg = f"Server side error occurs: {response.text}"
      logger.error(err_msg)
      raise ServerError(err_msg)  
