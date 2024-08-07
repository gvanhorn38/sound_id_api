# Sound ID API

This repo contains code for interacting with the Sound ID API. 


## Installation

You need to clone the repo, create a virtual environment, and install the requirements. 
```sh
git clone https://github.com/gvanhorn38/sound_id_api.git
cd sound_id_api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Example Usage

For convenience, you should create two environment variables that store the API URL and your API key. 
```sh
export API_URL=https://sound-id-api/tasks
export API_KEY=XXX
```

In all of the following examples, you must provide location and date information.

### Analyze a Local Audio File
You can submit an audio file that is < 6MB. The following command will submit the audio file for analysis and then will poll the API until the analysis finishes. 
```sh
python analyze.py \
--api_url=$API_URL \
--api_key=$API_KEY \
--audio_file_path=/Users/merlin/Downloads/vocalization.mp3 \
--latitude=42.375003 \
--longitude=-72.491837 \
--datetime=2024-05-01
```

### Analyze a Web Accessible Audio File
You can analyze a web accessible audio file that is < 4GB. The following command will submit the URL for analysis and then will poll the API until the analysis finishes. 
```sh
python analyze.py \
--api_url=$API_URL \
--api_key=$API_KEY \
--url=https://sound-id/merlin/vocalization.mp3 \
--latitude=42.375003 \
--longitude=-72.491837 \
--datetime=2024-05-01
```

### Analyze a Macaulay Library Audio File
The following command is convenient for processing a specific asset from the Macaulay Library
```sh
python analyze_ml.py \
--api_url=$API_URL \
--api_key=$API_KEY \
--asset_id=XXX
```

## Low Level Usage
You can POST and GET a task separately if you want to handle the polling yourself. If successful, `post_task.py` will output a task identifier that you need to provide to `get_task.py`. You will need to repeatedly call `get_task.py` until the task finishes. This example submits a local audio file, but you can also submit a URL. 
```sh
# If successful, this will output a task identifier
python post_task.py \
--api_url=$API_URL \
--api_key=$API_KEY \
--audio_file_path=/Users/merlin/Downloads/vocalization.mp3 \
--latitude=42.375003 \
--longitude=-72.491837 \
--datetime=2024-05-01

# Pass the task identifier to this command. 
# This might need to be called multiple times depending on how fast the task analysis finishes.
python get_task.py \
--api_url=$API_URL \
--api_key=$API_KEY \
--task_id=TTTTTTTT-TTTT-TTTT-TTTT-TTTTTTTTTTTT
```

## Command Line Usage for Linux

Submit a file.
```sh
curl -X POST "$API_URL" \
-H "x-api-key: $API_KEY" \
-H "content-type: multipart/form-data" \
-F "json={\"latitude\":42.375003,\"longitude\":-72.491837,\"datetime\":\"2024-05-01T06:36\"};type=application/json" \
-F "audioFile=@/Users/merlin/Downloads/vocalization.mp3;type=audio/mpeg"

# Pass the task identifier to this command.
curl -X GET "$API_URL/TTTTTTTT-TTTT-TTTT-TTTT-TTTTTTTTTTTT" \
-H "x-api-key: $API_KEY" 
```

Submit a url.
```sh
curl -X POST "$API_URL" \
-H "x-api-key: $API_KEY" \
-H "content-type: application/json" \
-d '{"url": "https://sound-id/merlin/vocalization.mp3", "latitude": 42.375003, "longitude": -72.491837, "datetime": "2024-05-01T06:36"}'

# Pass the task identifier to this command.
curl -X GET "$API_URL/TTTTTTTT-TTTT-TTTT-TTTT-TTTTTTTTTTTT" \
-H "x-api-key: $API_KEY"
```
