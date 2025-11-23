import json
import requests

import rstv_config

channels = {
    'RSTV1': {
        'chat': 'https://live.retrostrange.com/embed/chat/readwrite',
        'stream': 'https://live.retrostrange.com/hls/stream.m3u8',
        'nowplaying_path': '{}rstv1-nowplaying.txt'.format(rstv_config.nowplaying_status_path),
        'output_path': '{}rstv1-nowplaying.json'.format(rstv_config.nowplaying_status_path),
        'api_status_url': 'https://live.retrostrange.com/api/status',
        'api_status': {},
        'nowplaying_status': {}
    },
}

def text_to_json(input_file):
    # Read the lines from the text file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Ensure there are exactly two lines in the file
    if len(lines) != 2:
        raise ValueError("Input file must contain exactly two lines.")

    # Split the second line on the '/' character
    time_parts = lines[1].strip().split('/')
    if len(time_parts) != 2:
        raise ValueError("The second line must contain exactly one '/' character separating 'remaining' and 'duration'.")

    # Create a dictionary with the desired keys and values
    data = {
        'nowplaying': lines[0].strip(),
        'remaining': time_parts[0].strip(),
        'duration': time_parts[1].strip()
    }
    
    return data
        
def fetch_json_array(url):
    try:
        # Send GET request to the URL
        response = requests.get(url)
    
        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Attempt to parse JSON and convert to array
                data_array = response.json()
                # print("Successfully fetched JSON array:")
                # print(data_array)
                return data_array
            except ValueError as json_error:
                print(f"Error parsing JSON: {json_error}")
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as request_error:
        print(f"An error occurred during the request: {request_error}")

for item in channels:
    channel = channels[item]
    # Convert the text file to a JSON file
    nowplaying_status_data = text_to_json(channel['nowplaying_path'])
    api_status_data = fetch_json_array(channel['api_status_url'])
    
    if "viewerCount" in api_status_data:
        nowplaying_status_data['viewerCount'] = api_status_data['viewerCount']
    else:
        nowplaying_status_data['viewerCount'] = 0
    
    nowplaying_status_data['online'] = api_status_data['online']
    
    nowplaying_status_data['chat'] = channel['chat']
    nowplaying_status_data['stream'] = channel['stream']
    
    # Write the dictionary to a JSON file
    with open(channel['output_path'], 'w') as json_file:
        json.dump(nowplaying_status_data, json_file, indent=4)