import os
import json
import logging
import requests
from requests.auth import HTTPBasicAuth
import concurrent.futures
import argparse

def get_confluence_env():
    """Retrieve environment variables for Confluence."""
    return {
        "space": os.getenv('CONFLUENCE_SPACE'),
        "email": os.getenv('CONFLUENCE_EMAIL'),
        "instance": os.getenv('CONFLUENCE_INSTANCE'),
        "api_token": os.getenv('CONFLUENCE_TOKEN'),
    }

def read_html_from_file(file_path):
    """Read HTML content from a local file."""
    logging.debug(f"Reading HTML from file: {file_path}")
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")

def get_confluence_page_url(page_id: str, instance: str):
    """Construct the Confluence API URL to fetch the page content."""
    return f"https://{instance}.atlassian.net/wiki/rest/api/content/{page_id}"

def fetch_confluence_page(url, auth):
    """Fetch the current version of a Confluence page."""
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch the page: {response.status_code} - {response.text}")

def update_confluence_page(page_id, html_content, current_version, page_title, instance):
    """Update a Confluence page with new HTML content."""
    url = get_confluence_page_url(page_id, instance)
    confluence_env = get_confluence_env()

    # Prepare data for updating the page
    data = {
        "version": {"number": current_version + 1},
        "title": page_title,
        "type": "page",
        "space": {"key": confluence_env["space"]},
        "body": {
            "storage": {
                "value": html_content,
                "representation": "storage"
            }
        }
    }

    auth = HTTPBasicAuth(confluence_env["email"], confluence_env["api_token"])
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, json=data, auth=auth, headers=headers)

    if response.status_code == 200:
        return "Page updated successfully."
    else:
        raise Exception(f"Failed to update the page: {response.status_code} - {response.text}")

def process_page_update(item, path_prefix):
    """Process page updates for each item in the JSON."""
    logging.basicConfig(level=logging.DEBUG)
    
    logging.debug(f"Prefix: {path_prefix}")
    html_file = os.path.join(path_prefix, item["HTML"])
    page_id = item["ID"]

    logging.debug(f"Processing {page_id} - {html_file}")

    # Read the HTML content from the file
    try:
        html_content = read_html_from_file(html_file)
    except Exception as e:
        return f"Error reading HTML for page {page_id}: {e}"

    # Get environment variables and set up authentication
    confluence_env = get_confluence_env()
    auth = HTTPBasicAuth(confluence_env["email"], confluence_env["api_token"])
    instance = confluence_env["instance"]

    # Get the current version of the page
    url = get_confluence_page_url(page_id, instance)
    try:
        page_data = fetch_confluence_page(url, auth)
        current_version = page_data['version']['number']
        page_title = page_data['title']
        instance = confluence_env["instance"]
        logging.info("Instance: " + instance)
        
        # Update the page with the new HTML content
        result = update_confluence_page(page_id, html_content, current_version, page_title, instance)
        logging.info(f"Page {page_id} updated successfully: {result}")
        return f"Page {page_id} updated successfully: {result}"
    except Exception as e:
        return f"Error updating page {page_id}: {e}"

def load_html_to_ids(file_path):
    """Load the JSON file containing HTML file paths and corresponding Confluence page IDs."""
    logging.debug(f"Loading JSON from: {file_path}")
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except Exception as e:
        raise Exception(f"Error loading JSON file {file_path}: {e}")

def parallel_confluence_html_updates(input_file, path_prefix):
    """Parallelize the upload of HTML files to Confluence pages."""
    logging.debug(f"Loading HTML to ID mappings from: {input_file}")
    html_to_ids = load_html_to_ids(input_file)

    logging.debug(f"Loaded HTML to ID mappings: {html_to_ids}")

    # Parallelize the upload of HTML files to Confluence pages
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_page_update, item, path_prefix) for item in html_to_ids]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                logging.info(result)
            except Exception as e:
                logging.error(f"Error in page update: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Confluence pages with new HTML content.")
    parser.add_argument("-i", "--input", required=True, help="Path to the JSON file with HTML and page ID mappings")
    parser.add_argument("-p", "--prefix", required=False, help="Path prefix", default="")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    
    parallel_confluence_html_updates(args.input, args.prefix)
