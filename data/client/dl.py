import os
import json
import requests
from urllib.parse import urlparse
from pathlib import Path

def download_file(url, dest_path):
    # Make sure the target directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download the file and write it to the specified destination
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {url} -> {dest_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def find_and_download_urls(json_data):
    # If the data is a dictionary or list, we need to iterate over it
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, str) and urlparse(value).scheme in ['http', 'https']:
                # Create the target path in the resource directory
                url = value
                parsed_url = urlparse(url)
                path = parsed_url.path.lstrip('/')
                resource_path = Path('resource') / path
                
                # Download the file
                download_file(url, resource_path)
            elif isinstance(value, (dict, list)):
                # Recursively process nested objects or lists
                find_and_download_urls(value)
    elif isinstance(json_data, list):
        for item in json_data:
            if isinstance(item, dict):
                find_and_download_urls(item)

def process_file(json_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Process the JSON data to find URLs
        find_and_download_urls(data)
                
    except json.JSONDecodeError:
        print(f"Skipping invalid JSON file: {json_file}")
    except Exception as e:
        print(f"Error processing {json_file}: {e}")

def process_directory(cwd):
    # Walk through the current working directory
    for root, _, files in os.walk(cwd):
        for file in files:
            if file.endswith('.json'):
                json_file = os.path.join(root, file)
                process_file(json_file)

if __name__ == "__main__":
    cwd = os.getcwd()  # Current working directory
    process_directory(cwd)
