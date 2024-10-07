import argparse
import mimetypes
import os

import requests
from models import Task


MAX_REQUEST_SIZE_MB = 6
MAX_REQUEST_SIZE_BYTES = int(MAX_REQUEST_SIZE_MB * 1024 * 1024)

ALLOWED_AUDIO_FORMATS = {
    'audio/mpeg3': '.mp3',
    'audio/mpeg': '.mp3',
    'audio/wav': '.wav',
    'audio/x-wav': '.wav',
    'audio/aac': '.aac',
    'audio/flac': '.flac',
    'audio/x-flac': '.flac',
    'audio/x-m4a': '.m4a',
    'audio/ogg': '.ogg',
    'audio/x-ms-wma': '.wma',
    'audio/aiff': '.aiff',
    'audio/x-aiff': '.aif',
    'audio/opus': '.opus',
    'audio/amr': '.amr',
    'audio/mp4': '.m4a',
    'audio/mp4a-latm' : '.m4a'
}

def post_task(api_url, api_key, url, audio_file_path, latitude, longitude, datetime, include_species_codes=None):
    
    task_id = None

    # Make sure we have something to analyze.
    if url is None and audio_file_path is None:
        print("You must provide either a URL or an audio file path.")
        return task_id
    
    headers = {
        'x-api-key': api_key
    }

    data = {
        'latitude': latitude,
        'longitude': longitude,
        'datetime': datetime,
        'include_species_codes': include_species_codes,
    }

    if url:
        data['url'] = url

        # Validate the data (the server will do this too, but might as well have the client do it too)
        task = Task(**data)
        task_json_str = task.model_dump_json()
        response = requests.post(api_url, headers=headers, data=task_json_str)
    
    elif audio_file_path:
        
        task = Task(**data)
        task_json_str = task.model_dump_json()

        audio_file_size = os.path.getsize(audio_file_path)
        
        # Calculate the total size of the request
        size_of_request = audio_file_size + len(task_json_str)
        if size_of_request > MAX_REQUEST_SIZE_BYTES:
            print(f"The request size (mainly audio file size) exceeds the limit of {MAX_REQUEST_SIZE_MB} MB.")
            return task_id
        
        # Make sure the mime type for the file is a supported audio type
        mime_type, _ = mimetypes.guess_type(audio_file_path, strict=False)
        assert mime_type in list(ALLOWED_AUDIO_FORMATS.keys()), f"The file MIME type {mime_type} is not supported."

        with open(audio_file_path, 'rb') as f:
            
            files = {
                'json' : (None, task_json_str, 'application/json'),
                'audioFile': (os.path.basename(audio_file_path), f, mime_type)
            }
            response = requests.post(api_url, headers=headers, files=files)

    if response.status_code != 201:
        print(f"Failed to submit task, the server responded with status code: {response.status_code}")
        print(response.json())
    else:
        task_id = response.json()['id']

    return task_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post a task to the API")
    parser.add_argument('--api_url', type=str, required=True, help="API URL")
    parser.add_argument('--api_key', type=str, required=True, help="API key")
    parser.add_argument('--url', type=str, help="URL of the audio file", default=None)
    parser.add_argument('--audio_file_path', type=str, help="Path to the audio file", default=None)
    parser.add_argument('--latitude', type=float, required=True, help="Latitude")
    parser.add_argument('--longitude', type=float, required=True, help="Longitude")
    parser.add_argument('--datetime', type=str, required=True, help="Datetime in ISO format")

    args = parser.parse_args()
    task_id = post_task(args.api_url, args.api_key, args.url, args.audio_file_path, args.latitude, args.longitude, args.datetime)

    if task_id is not None:
        print(f"Task Submitted: {task_id}")