import json
import os

# Filepath
input_filepath = r"/temp.json"
output_filepath = r"/temp_updated.json"

# Read the JSON file
with open(os.getcwd() + input_filepath, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Increment every "c" value by 1000
for item in data:
    item["c"] += 2000

# Save the updated JSON
with open(os.getcwd() + output_filepath, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Updated JSON saved to {output_filepath}")