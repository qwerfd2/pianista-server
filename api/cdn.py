import os
import json
import re

def update_configs(url):
    print("[CONFIG] Updating URLs in config files to", url)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_cwd = os.path.abspath(os.path.join(script_dir, '..'))
    
    directories = [
        os.path.join(project_cwd, "bundle"),
        os.path.join(project_cwd, "data", "client", "app_store", "1"),
        os.path.join(project_cwd, "data", "client", "google_play", "1"),
        os.path.join(project_cwd, "data", "client", "common", "1"),
        os.path.join(project_cwd, "manifest")
    ]
    
    url_pattern = re.compile(r'http[s]?://[^/]+')
    
    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                updated_data = update_urls_in_dict(data, url, url_pattern)
                
                with open(filepath, 'w', encoding='utf-8') as file:
                    json.dump(updated_data, file, ensure_ascii=False, indent=4)

    print("[CONFIG] URLs updated successfully")

def update_urls_in_dict(data, new_url, url_pattern):
    if isinstance(data, dict):
        return {key: update_urls_in_dict(value, new_url, url_pattern) for key, value in data.items()}
    elif isinstance(data, list):
        return [update_urls_in_dict(item, new_url, url_pattern) for item in data]
    elif isinstance(data, str):
        return url_pattern.sub(new_url.rstrip('/'), data)
    else:
        return data
