def export_xml_to_json(xml_file, json_file):
    """Convert a single XML file to a JSON file."""
    import xmltodict
    import json
    with open(xml_file, 'r', encoding='utf-8') as file:
        xml_content = file.read()
        data_dict = xmltodict.parse(xml_content)

    with open(json_file, 'w', encoding='utf-8') as jsonf:
        json.dump(data_dict, jsonf, indent=4)

def process_xml_to_json_files(input_dir, output_dir, extension):
    """Process files with the specified extension in the input directory and save them as JSON in the output directory."""
    import os
    from concurrent.futures import ThreadPoolExecutor
    import logging
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.debug(f"Created output directory: {output_dir}")
    
    # Find files with the given extension in the input directory
    files = [f for f in os.listdir(input_dir) if f.endswith(extension)]
    logging.debug(f"Found {len(files)} files with extension {extension} in {input_dir} - {files}")

    with ThreadPoolExecutor() as executor:
        for file in files:
            file_path = os.path.join(input_dir, file)
            json_filename = os.path.splitext(file)[0] + '.json'
            json_path = os.path.join(output_dir, json_filename)
            
            # Submit each file for parallel processing
            executor.submit(export_xml_to_json, file_path, json_path)

    logging.info(f"Converted {len(files)} files to JSON in {output_dir}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert files to JSON")
    parser.add_argument('--input_dir', '-i', help="Directory containing files")
    parser.add_argument('--output_dir', '-o', help="Directory to save JSON files")
    parser.add_argument('--extension', '-e', default='.xml', help="File extension to process (default: .xml)")
    
    args = parser.parse_args()
    
    # Process the files with the specified extension and convert them to JSON in parallel
    process_xml_to_json_files(args.input_dir, args.output_dir, args.extension)
