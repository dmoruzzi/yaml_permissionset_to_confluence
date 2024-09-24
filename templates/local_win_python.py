{#
#
#    python_text = inject_py_file(python_text, 'scripts/xml_to_json.py')
#    python_text = inject_py_file(python_text, 'scripts/json_to_html.py')
#    python_text = inject_py_file(python_text, 'scripts/read_confluence_db.py')
#    python_text = inject_py_file(python_text, 'scripts/update_confluence.py')
#    python_text = inject_py_file(python_text, 'scripts/compare_delta.py')
#
#}

if __name__ == "__main__":
    import os
    import logging
    from pathlib import Path

    logging.basicConfig(level=logging.DEBUG)

    os_ver = os.popen("ver").read()
    if "Microsoft Windows" in os_ver:
        logging.info("Windows OS detected")
    else:
        raise Exception("Windows OS is not detected")


    {%- if sf_install %}
    # Check if Salesforce CLI is installed
    exec_cmd = "sf --version"
    logging.debug(f"Running command: {exec_cmd}")
    output = os.popen(exec_cmd).read()
    logging.debug(f"Command output: {output}")
    if "@salesforce/cli" in output:
        logging.info("Salesforce CLI is installed")
    else:
        raise Exception("Salesforce CLI is not installed")
    {%- endif %}

    # Make empty SF project
    {%- if sf_empty_project %}
    exec_cmd = "sf project generate --name {{ sf_empty_project[0].name | default("salesforce") }} --template {{ sf_empty_project[0].template | default('empty') }}"
    logging.debug(f"Running command: {exec_cmd}")
    output = os.popen(exec_cmd).read()
    logging.debug(f"Command output: {output}")
    {%- endif %}

    # Switch to project directory
    dist_dir = f"{os.getcwd()}"
    sf_dir = f"{dist_dir}/{{ sf_empty_project[0].name | default('salesforce') }}"
    os.chdir(Path(sf_dir))

    # Download Metadata
    {%- if SF_METADATA_DOWNLOAD %}
    {%- for metadata in SF_METADATA_DOWNLOAD %}
    exec_cmd = 'sf project retrieve start --metadata "{{ metadata.metadata }}" -o {{ metadata.org }} --ignore-conflicts --json'
    logging.debug(f"Running command: {exec_cmd}")
    output = os.popen(exec_cmd).read()
    with open('{{ metadata.org }}-permissionset.json', 'w') as f:
        f.write(output)
    logging.debug(f"Command output: {output}")
    {%- endfor %}
    {%- endif %}

    # XML path
    permissionset_xml_dir = f"{sf_dir}/force-app/main/default/permissionsets"

    # Convert XML to JSON
    permissionset_json_dir = f"{sf_dir}/permset-json"
    process_xml_to_json_files(Path(permissionset_xml_dir), Path(permissionset_json_dir), ".permissionset-meta.xml")

    # Convert JSON to HTML
    permissionset_html_dir = f"{sf_dir}/permset-html"
    process_json_to_html_files(Path(permissionset_json_dir), Path(permissionset_html_dir), ".permissionset-meta.json", "{{ SF_ORG }}")

    # Read Confluence DB
    get_webpage(page_id="{{ CONFLUENCE_MASTER_ID}}", output="html_to_ids.json")

    # Update Confluence pages
    parallel_confluence_html_updates("html_to_ids.json", "./permset-html/")

    # Compare Delta
    calculate_diffs(input_dir="permset-html", map_file="html_to_ids.json", output="differences.json")