from os.path import exists

import errors
import json
import logging
import requests

logger = logging.getLogger('auth_api')
JWT_STORAGE_DEFAULT_PATH = '/tmp/space_know_token'

class AuthApi():
    '''
    Spaceknow auth api handler
    '''

    def __init__(self, auth_endpoint: str, username: str, password: str):
        self.auth_endpoint = auth_endpoint
        self.__username = username
        self.__password = password
        self.__id_token = None

    def __authorize(self, headers: dict, force: bool = False) -> dict: 
        logger.debug("Trying to authorize request")
        id_token = None
    
        if self.__id_token and not force:
            logger.debug("Using cached ID token for request authentication")
            id_token = self.__id_token
        elif exists(JWT_STORAGE_DEFAULT_PATH) and not force: 
        # load token from local 
            logger.debug(f"Using local {JWT_STORAGE_DEFAULT_PATH} ID token for request authentication")
     
        try: 
            with open(JWT_STORAGE_DEFAULT_PATH, 'r') as f:
                auth_response = json.loads(f.read())
                id_token = auth_response['id_token']
        except Exception as e: 
            logger.error(f"Can't read token from local storage {JWT_STORAGE_DEFAULT_PATH}: {str(e)}")
            self.__authorize(headers, force=True)
        
        else:
          # request token
            logger.debug(f"Requesting ID token from auth endpoint {self.auth_endpoint}")
            auth_response = self.__request_JWT()
        
          # save token to local
            with open(JWT_STORAGE_DEFAULT_PATH, 'w') as f:
                f.write(json.dumps(auth_response)) # TODO base64
          
            id_token = auth_response['id_token'] 
          
            headers['Authorization'] = f"Bearer {id_token}"
    
    
    def __check_response_status_code(self, response):
        if response.status_code >= 400 and response.status_code <= 499:
            err_msg = f"Client side error occurs: {response.text}"
            logger.error(err_msg)
            raise errors.ClientError(err_msg)
    
        if response.status_code >= 500 and response.status_code <= 599:
            err_msg = f"Server side error occurs: {response.text}"
            logger.error(err_msg)
            raise errors.ServerError(err_msg)  
    
    
    def __request_JWT(self) -> json:
        request_body = {
          "client_id": "hmWJcfhRouDOaJK2L8asREMlMrv3jFE1",
          "username": self.__username,
          "password": self.__password,
          "connection": "Username-Password-Authentication",
          "grant_type": "password",
          "scope": "openid"
        }
    
        response = requests.post(self.auth_endpoint, json=request_body)
        logger.debug(f"Auth response status code {response.status_code}")
    
        self.__check_response_status_code(response)
        logger.debug("Token request successfull from auth endpoint {self.auth_endpoint}")
        return response.json()
      
    def request(self, api_url: str, data: dict) -> json:     
        request_headers = {
          'Host': 'api.spaceknow.com'
        }
    
        self.__authorize(request_headers)
        response = requests.post(api_url, headers=request_headers, json=data)
    
        response_ready_log = f"Api request complete with status code: {response.status_code}"
        logger.info(response_ready_log)
    
        if response.status_code >= 400 and response.status_code <= 499:
          # handling token expiration
            err_msg = response.json().get('errorMessage', None)
            if (err_msg and "Signature has expired" in err_msg):
              # expired JWT token, ask for the new one
                logger.info('JWT token has expired, asking for the new one')
                self.__authorize(headers={}, force=True) # just dummy call for token recreation
                return self.request(api_url, data) 
    
        self.__check_response_status_code(response)
        return response.json()
    