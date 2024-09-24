
def get_confluence_env():
    """Retrieve environment variables for Confluence."""
    import os
    return {
        "space": os.getenv('CONFLUENCE_SPACE'),
        "email": os.getenv('CONFLUENCE_EMAIL'),
        "instance": os.getenv('CONFLUENCE_INSTANCE'),
        "api_token": os.getenv('CONFLUENCE_TOKEN'),
    }

def get_confluence_content_page_url(page_id: str, instance: str):
    """Construct the Confluence API URL to fetch the page content."""
    return f"https://{instance}.atlassian.net/wiki/rest/api/content/{page_id}?expand=body.storage"

def fetch_confluence_page(url, auth):
    """Fetch the Confluence page and return the response data."""
    import requests
    
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch the page: {response.status_code} - {response.text}")

def get_page_html_content(page_data):
    """Extract the HTML body content from the fetched page data."""
    return page_data['body']['storage']['value']

def parse_table_to_dict(html_content):
    """Parse the HTML content for table(s) and convert them to a JSON-compatible dictionary."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')  # Assumes there is at least one table in the content

    if not table:
        raise ValueError("No table found in the HTML content")

    headers = [header.get_text(strip=True) for header in table.find_all('th')]
    rows = []
    
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cells = [cell.get_text(strip=True) for cell in row.find_all('td')]
        if len(cells) == len(headers):  # Ensure row has the correct number of cells
            rows.append(dict(zip(headers, cells)))

    return rows

def get_webpage(page_id: str, output: str):
    import logging
    from requests.auth import HTTPBasicAuth
    import json

    logging.basicConfig(level=logging.DEBUG)

    # Get environment variables
    confluence_env = get_confluence_env()
    
    # Build the API URL
    url = get_confluence_content_page_url(page_id=page_id, instance=confluence_env["instance"])
    
    # Authentication
    auth = HTTPBasicAuth(confluence_env["email"], confluence_env["api_token"])
    
    try:
        # Fetch the Confluence page
        page_data = fetch_confluence_page(url, auth)
        
        # Extract and print the HTML body content
        html_body = get_page_html_content(page_data)
        json_data = parse_table_to_dict(html_body)
        logging.debug(f'JSON Data: {json_data}')
        json.dump(json_data, open(output, 'w'))
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--page_id", required=False, help="Confluence page ID",default="9994318")
    parser.add_argument("-o", "--output", required=False, help="Output file path", default="html_to_ids.json")
    args = parser.parse_args()

    get_webpage(page_id=args.page_id, output=args.output)
