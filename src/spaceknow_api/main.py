from apis.task_api import TaskApi
from apis.auth_api import AuthApi
from argparse import ArgumentError
from tasks.kraken_task import KrakenTask
from tasks.ragnar_task import RagnarTask

import geojson
import getpass
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')

def main():  
    username = input('Username: ')
    if not username:
        raise ArgumentError("Invalid username")
    
    password = getpass.getpass()
    if not password:
        raise ArgumentError("Invalid password")
    
    input_geojson = input("Input geojson path (default input.geojson): ") or "input.geojson"
    
    logger.info(f"Starting app, username: {username}")
    
    extent = None
    with open(input_geojson, 'r') as f:
        extent = geojson.loads(f.read())
    if not extent:
         raise ArgumentError("Invalid geojson input")
    
    auth_api = AuthApi('https://spaceknow.auth0.com/oauth/ro', username, password) #TODO username pass 
    task_api = TaskApi('https://api.spaceknow.com/tasking/get-status', auth_api)
  
    # run Ragnar task, search imagery
    logger.info("Going to RAGNAR stage")
    ragnar_task = RagnarTask(auth_api, task_api)
    ragnar_task.initiate_with_default(extent)

    # wait when ready
    while not ragnar_task.completed:
        logger.debug("Waiting for Ragnar api...")
        time.sleep(2)
    scene_ids = ragnar_task.retreive_scene_ids()
  
    # run analysis, Kraken task
    logger.info("Going to KRAKEN stage")
    kraken_task = KrakenTask(auth_api, task_api)
    kraken_task.initiate_with_default(scene_ids, extent)
    
    # wait when ready
    while not kraken_task.completed:
        logger.debug("Waiting for Kraken api...")
        time.sleep(2)
        
    print(kraken_task.retreive())
    
    # Get results from datacube
    # Get grid files
  
if __name__ == "__main__":
  main()
