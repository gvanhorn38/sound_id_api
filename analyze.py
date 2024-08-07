"""
Driver for both POST and GET. 
"""

import argparse
import datetime
import time

import get_task
import post_task
import utils


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post a task to the API")
    parser.add_argument('--api_url', type=str, required=True, help="API URL")
    parser.add_argument('--api_key', type=str, required=True, help="API key")
    parser.add_argument('--url', type=str, help="URL of the audio file", default=None)
    parser.add_argument('--audio_file_path', type=str, help="Path to the audio file", default=None)
    parser.add_argument('--latitude', type=float, required=True, help="Latitude")
    parser.add_argument('--longitude', type=float, required=True, help="Longitude")
    parser.add_argument('--datetime', type=str, required=True, help="Datetime in ISO format")
    parser.add_argument('--output_fp', type=str, help="(Optional) File path to save the detection results.", default=None)

    args = parser.parse_args()
    
    start_time = datetime.datetime.now()

    task_id = post_task.post_task(
        args.api_url, args.api_key, 
        args.url, args.audio_file_path, 
        args.latitude, args.longitude, args.datetime
    )
    if task_id is not None:
        
        print(f"Task Submitted: {task_id}")

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