import argparse
import os

import pandas as pd
import requests

from models import TaskStatus
from utils import urljoin

TASK_STATUS_QUEUED = 'QUEUED'
TASK_STATUS_IN_PROGRESS = 'IN_PROGRESS'
TASK_STATUS_SUCCESS = 'SUCCESS'
TASK_STATUS_FAIL = 'FAIL'

def get_task_status(api_url, api_key, task_id):
    
    task_status = None
    
    headers = {
        'x-api-key': api_key
    }
    url = urljoin(api_url, task_id)
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch task status, the server responded with status code: {response.status_code}")
        print(response.json())
    else:
        #print(response.json())
        task_status = TaskStatus(**response.json())    

    return task_status

def handle_task_status(task_status, output_fp=None):

    finished = False

    if task_status.status == TASK_STATUS_QUEUED:
        print("Task is queued for processing.")

    elif task_status.status == TASK_STATUS_IN_PROGRESS:
        print("Task is currently running.")

    elif task_status.status == TASK_STATUS_SUCCESS:
        print("Task succeeded.")
        print(f"Audio duration (seconds): {task_status.audio_duration}")
        detections_df = pd.DataFrame(task_status.dict().get('detections', []))
        if output_fp is not None:
            detections_df.to_csv(output_fp, index=False)
        else:
            print(detections_df.to_string())
        
        finished = True

    elif task_status.status == TASK_STATUS_FAIL:
        print("Task failed.")
        print(task_status.message)
        finished = True

    else:
        print("Unknown task status.")
        finished = True

    return finished


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get the status of a task from the API")
    parser.add_argument('--api_url', type=str, help="API URL")
    parser.add_argument('--api_key', type=str, help="API key")
    parser.add_argument('--task_id', type=str, help="ID of the task")
    parser.add_argument('--output_fp', type=str, help="(Optional) File path to save the detection results.", default=None)

    args = parser.parse_args()
    task_status = get_task_status(args.api_url, args.api_key, args.task_id)
    if task_status is not None:
        task_finished = handle_task_status(task_status, args.output_fp)