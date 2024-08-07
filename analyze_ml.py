

import argparse
import datetime
import re
import time

from bs4 import BeautifulSoup
import requests

import get_task
import post_task
import utils

def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def fetch_asset_details(html_content):

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the date
    date_element = soup.find('time')
    date_string = date_element['datetime'] if date_element else None
    if date_string is None:
        raise Exception("Failed to parse date.")

    # Extract the coordinates
    coords_text = soup.find(text=re.compile(r'Coordinates:'))
    coords_string = coords_text.find_next('span').text.strip() if coords_text else None

    # Convert coordinates to floats
    if coords_string:
        latitude, longitude = map(float, coords_string.split(','))
    else:
        raise Exception("Failed to parse location coordinates.")

    return date_string, latitude, longitude


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post a task to the API")
    parser.add_argument('--api_url', type=str, required=True, help="API URL")
    parser.add_argument('--api_key', type=str, required=True, help="API key")
    parser.add_argument('--asset_id', type=int, help="Macaulay Library Asset ID", default=None)
    parser.add_argument('--output_fp', type=str, help="(Optional) File path to save the detection results.", default=None)

    args = parser.parse_args()
    
    asset_id = args.asset_id
    asset_url = f"https://macaulaylibrary.org/asset/{asset_id}"
    asset_html = fetch_html(asset_url)
    date_string, latitude, longitude = fetch_asset_details(asset_html)

    # Print results
    print(f"Date: {date_string}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")

    asset_audio_url = f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset_id}/audio"

    start_time = datetime.datetime.now()

    task_id = post_task.post_task(
        args.api_url, args.api_key, 
        asset_audio_url, None, 
        latitude, longitude, date_string
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