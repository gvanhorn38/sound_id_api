import argparse
import datetime
import time

import requests
from bs4 import BeautifulSoup

import get_task
import post_task
import utils

def fetch_html(url):
    """
    Downloads the HTML content from the Xeno Canto page.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def fetch_xc_details(html_content):
    """
    Parses the Xeno Canto HTML page to extract the date, time, latitude, longitude, and audio file download URL.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the date and time
    date_element = soup.find('td', string='Date').find_next_sibling('td')
    time_element = soup.find('td', string='Time').find_next_sibling('td')
    
    date_string = date_element.text if date_element else None
    time_string = time_element.text if time_element else None
    
    if not date_string or not time_string:
        raise Exception("Failed to parse date or time.")
    
    # Combine date and time into a datetime object
    datetime_str = f"{date_string} {time_string}"
    datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

    # Extract the latitude and longitude
    latitude_element = soup.find('td', string='Latitude').find_next_sibling('td')
    longitude_element = soup.find('td', string='Longitude').find_next_sibling('td')

    latitude = float(latitude_element.text) if latitude_element else None
    longitude = float(longitude_element.text) if longitude_element else None
    
    if latitude is None or longitude is None:
        raise Exception("Failed to parse location coordinates.")

    return datetime_obj, latitude, longitude

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post a task to the API using Xeno Canto observation data")
    parser.add_argument('--api_url', type=str, required=True, help="API URL")
    parser.add_argument('--api_key', type=str, required=True, help="API key")
    parser.add_argument('--xc_id', type=int, required=True, help="Xeno Canto Asset ID")
    parser.add_argument('--include_species_codes', type=str, help="Space-separated list of eBird species codes to include in the analysis", default=None)
    parser.add_argument('--output_fp', type=str, help="(Optional) File path to save the detection results.", default=None)

    args = parser.parse_args()
    
    xc_id = args.xc_id
    xc_url = f"https://xeno-canto.org/{xc_id}"
    
    # Fetch Xeno Canto page HTML
    xc_html = fetch_html(xc_url)

    # Extract date, location, and audio file URL from HTML
    datetime_obj, latitude, longitude = fetch_xc_details(xc_html)

    # Print results
    print(f"Date: {datetime_obj}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")

    audio_url =  f"https://xeno-canto.org/{xc_id}/download"
    
    # Handle the species codes that the user wants to include
    include_species_codes_str = args.include_species_codes
    if args.include_species_codes:
        include_species_codes = args.include_species_codes.split()
    else:
        include_species_codes = None

    start_time = datetime.datetime.now()

    # Call your custom API with the fetched data
    task_id = post_task.post_task(
        args.api_url, args.api_key, 
        audio_url, None, 
        latitude, longitude, datetime_obj.isoformat(), include_species_codes
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
