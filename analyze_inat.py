import argparse
import datetime
import time

import requests

import get_task
import post_task
import utils

def fetch_inat_observation(observation_id):
    """
    Fetches observation details from the iNaturalist API using the observation ID.
    """
    url = f"https://api.inaturalist.org/v1/observations/{observation_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch observation {observation_id}: {response.status_code}")
    
    data = response.json()
    if data['total_results'] == 0:
        raise Exception(f"No results found for observation {observation_id}")
    
    result = data['results'][0]
    
    # Extract important fields
    time_observed_at = result.get('time_observed_at')
    location = result.get('location').split(',')
    latitude = float(location[0])
    longitude = float(location[1])
    
    # Extract media (if any sounds are available)
    sounds = result.get('sounds', [])
    if not sounds:
        raise Exception(f"No sounds available for observation {observation_id}")
    
    audio_url = sounds[0].get('file_url')
    
    return time_observed_at, latitude, longitude, audio_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post a task to the API using iNaturalist observation data")
    parser.add_argument('--api_url', type=str, required=True, help="API URL")
    parser.add_argument('--api_key', type=str, required=True, help="API key")
    parser.add_argument('--obs_id', type=int, required=True, help="iNaturalist Observation ID")
    parser.add_argument('--output_fp', type=str, help="(Optional) File path to save the detection results.", default=None)

    args = parser.parse_args()
    
    observation_id = args.obs_id
    
    # Fetch observation details from iNaturalist
    time_observed_at, latitude, longitude, audio_url = fetch_inat_observation(observation_id)

    # Print fetched metadata
    print(f"Date: {time_observed_at}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")

    start_time = datetime.datetime.now()

    # Call your custom API with the fetched data
    task_id = post_task.post_task(
        args.api_url, args.api_key, 
        audio_url, None, 
        latitude, longitude, time_observed_at
    )
    
    if task_id is not None:
        print(f"Task Submitted: {task_id}")
        
        # Poll the task status until completion
        while True:
            time.sleep(1)

            task_status = get_task.get_task_status(
                args.api_url, args.api_key, 
                task_id
            )
            if task_status is not None:
                task_finished = get_task.handle_task_status(task_status, args.output_fp)
                if task_finished:
                    end_time = datetime.datetime.now()
                    utils.print_execution_time(end_time - start_time)
                    break
