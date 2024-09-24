import os
import json
import requests
import logging


def load_json(json_file):
    """Load the HTML to ID mappings from the JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def compare_files(html_dir, json_data):
    """Compare HTML files in the directory with the JSON file data."""
    html_files = set(f for f in os.listdir(html_dir) if f.endswith('.html'))
    json_files = set(entry['HTML'] for entry in json_data)

    # New HTML files
    new_files = html_files - json_files

    # Missing HTML files
    missing_files = json_files - html_files

    differences = []

    # Add new files to the output
    for new_file in new_files:
        differences.append({"status": "new", "file": new_file})

    # Add missing files to the output
    for missing_file in missing_files:
        differences.append({"status": "missing", "file": missing_file})

    return differences

def save_json(output_file, data):
    """Save the comparison results to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

def send_permission_set_change_alert(changes):
    """Send a notification if there are permission set changes."""
    message = f"Permission sets changed: {len(changes)} changes detected."
    ALERT_WEBBOOK = "http://alerts.dmoruzzi.com/c185ddac8b5a8f5aa23c5b80bc12d214"
    response = requests.post(ALERT_WEBBOOK, json={"message": message})
    if response.status_code == 200:
        logging.info(f'Successfully sent notification: {response.status_code} - {response.text}')
    else:
        logging.error(f'Failed to send notification: {response.status_code} - {response.text}')

def calculate_diffs(input_dir: str, map_file: str, output: str):
    logging.basicConfig(level=logging.INFO)

    # Load JSON data
    json_data = load_json(map_file)

    # Compare HTML files in the directory with JSON data
    differences = compare_files(input_dir, json_data)

    # Save the differences to the output JSON file
    save_json(output, differences)

    # Send notification if there are any differences
    if differences:
        send_permission_set_change_alert(differences)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare HTML files to JSON data.")
    parser.add_argument("-i", "input_dir", help="Input directory with HTML files")
    parser.add_argument("-m", "map_file", help="JSON file with HTML to ID mappings")
    parser.add_argument("-o", "--output", help="Output file for the differences", default="differences.json")
    args = parser.parse_args()

    calculate_diffs(input_dir=args.input_dir, map_file=args.map_file, output=args.output)
