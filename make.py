import jinja2
import os
import logging



def main():
    workflow_template = fetch_template(dir="templates", name="workflow.yml.jinja2")
    python_template = fetch_template(dir="templates", name="local_win_python.py")

    
    # Template context
    context = dict()
    context["workflow_name"] = 'Salesforce Permission Set Report'
    context["CONFLUENCE_MASTER_ID"] = "9994318"
    context["prefix"] = ' '*10
    context["python_version"] = '3.12'  
    context["sf_install"] = True
    context["sf_empty_project"] = [{
        "comment": "Create an empty project in Salesforce",
        "name": "salesforce",
    }]

    # Make directories
    context["mkdirs"] = []
    context["mkdirs"].append({
        "path": "$GITHUB_WORKSPACE/permset-html",
        "comment": "Directory to save HTML files"
    })
    context["mkdirs"].append({
        "path": "$GITHUB_WORKSPACE/permset-json",
        "comment": "Directory to save JSON files"
    })

    for d in context["mkdirs"]:
        if "name" not in d:
            d["name"] = os.path.basename(d["path"])

    # Python dependencies
    context['python_dependencies'] = []
    context['python_dependencies'].append({
        'version': '>=2.32.3,<3.0.0',
        'name': 'requests',
        'comment': 'HTTP library for Confluence APIs'
    })
    context['python_dependencies'].append({
        'version': '>=3.1.4,<4.0.0',
        'name': 'jinja2',
        'comment': 'Template engine for Confluence HTML reports'
    })
    context['python_dependencies'].append({
        'version': '=0.13.0',
        'name': 'xmltodict',
        'comment': 'XML library for converting XML Permissionsets to JSON'
    })
    context['python_dependencies'].append({
        "version": ">=4.12.3,<5.0.0",
        "name": "beautifulsoup4",
        "comment": "HTML Parser library for Confluence HTML to JSON"
    })

    # Cron schedule(s); empty if not needed
    context['scheduled'] = []
    # context['scheduled'].append({
    #     "cron": "* 7 * * 2",
    #     "comment": "Every Tuesday at 7 AM UTC"
    # })
    # context['scheduled'].append({
    #     "cron": "* 7 * * 4",
    #     "comment": "Every Thursday at 7 AM UTC"
    # })

    # Files to write
    context['files'] = []
    context['files'].append({
        "name": "XML to JSON",
        "path": "${{ GITHUB_WORKSPACE }}/xml_to_json.py",
        "comment": "This script converts XML files to JSON which can be used for easier table creation",
        "content": read_file_content("scripts/xml_to_json.py"),
    })
    context['files'].append({
        "name": "JSON to HTML",
        "path": "${{ GITHUB_WORKSPACE }}/json_to_html.py",
        "comment": "This script converts JSON files to HTML",
        "content": read_file_content("scripts/json_to_html.py"),
    })
    context['files'].append({
        "name": "Read Confluence DB",
        "path": "${{ GITHUB_WORKSPACE }}/read_confluence_db.py",
        "comment": "This script reads the latest Confluence ID from the Confluence Master Sheet",
        "content": read_file_content("scripts/read_confluence_db.py"),
    })
    context['files'].append({
        "name": "Update Confluence Pages",
        "path": "${{ GITHUB_WORKSPACE }}/update_confluence.py",
        "comment": "This script updates Confluence pages with new HTML content",
        "content": read_file_content("scripts/update_confluence.py"),
    })
    context['files'].append({
        "name": "Compare Delta",
        "path": "${{ GITHUB_WORKSPACE }}/compare_delta.py",
        "comment": "This script compares HTML files to JSON data",
        "content": read_file_content("scripts/compare_delta.py"),
    })

    context["execute_python"] = []
    context["execute_python"].append({
        "name": "XML to JSON",
        "comment": "Convert XML Permissionsets to JSON for table creation",
        "path": "./xml_to_json.py",
        "args": '-i "$GITHUB_WORKSPACE/salesforce/force-app/main/default/permissionsets" -o "$GITHUB_WORKSPACE/salesforce/permset"'
    })
    context["execute_python"].append({
        "name": "JSON to HTML",
        "comment": "Convert JSON Permissionsets to HTML",
        "path": "./json_to_html.py",
        "args": '-i "$GITHUB_WORKSPACE/salesforce/permset" -o "$GITHUB_WORKSPACE/permset-html"'
    })
    context["execute_python"].append({
        "name": "Read Confluence DB",
        "comment": "Retrieve the latest HTML to Confluence IDs from Confluence's Master Sheet",
        "path": "./read_confluence_db.py",
        "args": f'-p "{context["CONFLUENCE_MASTER_ID"]}" -o "$GITHUB_WORKSPACE/html_to_ids.json"'
    })
    context["execute_python"].append({
        "name": "Update Confluence Pages",
        "comment": "Parallelly update Confluence pages with new HTML content",
        "path": "./update_confluence.py",
        "args": '-i "$GITHUB_WORKSPACE/html_to_ids.json" -p "$GITHUB_WORKSPACE/permset-html/"'
    })
    context["execute_python"].append({
        "name": "Compare Delta",
        "comment": "Compare HTML files to JSON data",
        "path": "./compare_delta.py",
        "args": '-i "$GITHUB_WORKSPACE/permset-html" -m "$GITHUB_WORKSPACE/html_to_ids.json" -o "$GITHUB_WORKSPACE/differences.json"'
    })

    # Compress folders to make easier uploading for artifacts
    context["compress_folders"] = []
    context["compress_folders"].append({
        "comment": "Permissionset HTML files",
        "path": "permset-html",
        "target": "permset-html.tgz"
    })
    context["compress_folders"].append({
        "comment": "Permissionset JSON files",
        "path": "permset-json",
        "target": "permset-json.tgz"
    })
    context["compress_folders"].append({
        "comment": "XML Permissionset files",
        "path": "salesforce/force-app/main/default/permissionsets",
        "target": "permissionsets.tgz"
    })

    # Upload artifacts
    context["upload_artifacts"] = []
    context["upload_artifacts"].append({
        "path": "differences.json"
    })
    context["upload_artifacts"].append({
        "path": "permset-html.tgz"
    })
    context["upload_artifacts"].append({
        "path": "permset-json.tgz"
    })
    context["upload_artifacts"].append({
        "path": "permissionsets.tgz"
    })

    for d in context["upload_artifacts"]:
        if "/" in d["path"]:
            d["name"] = d["path"].split("/")[-1]
        else:
            d["name"] = d["path"]  # Handle case where there is no slash

        if "." in d["name"]:
            d["name"] = d["name"].split(".")[0]

    # SF Auth
    context["SF_AUTH"] = [{
        "secret_key": "AUTH_ACH01",
        "alias": "ACH01",
    }]
    
    # SF Download
    context["SF_METADATA_DOWNLOAD"] = [{
        "name": "Permissionsets",
        "org": "prim",
        "metadata": "PermissionSet:*"
    }]



    # Prepare the output
    stage_dist_dir()
    workflow_text = workflow_template.render(context)
    save_dist(output=workflow_text, file="workflow.yml")

    python_text = python_template.render(context)
    # Inject Python scripts into local Python workflow
    python_text = inject_py_file(python_text, 'scripts/xml_to_json.py')
    python_text = inject_py_file(python_text, 'scripts/json_to_html.py')
    python_text = inject_py_file(python_text, 'scripts/read_confluence_db.py')
    python_text = inject_py_file(python_text, 'scripts/update_confluence.py')
    python_text = inject_py_file(python_text, 'scripts/compare_delta.py')
    save_dist(output=python_text, file="local_win_python.py")

def inject_py_file(python_text: str, file: str):

    with open(file, 'r') as f:
        inject_text = f.read().split('if __name__ == "__main__":')
    python_text = inject_text[0] + python_text
    return python_text


def fetch_template(dir: str = "templates", name: str = "workflow.yml.jinja2") -> jinja2.Template:
    template_dir = os.path.join(os.path.dirname(__file__), dir)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    return env.get_template(name)

def save_dist(output: str, file: str):
    with open(f'dist/{file}', 'w') as f:
        f.write(output)

def stage_dist_dir():
    os.makedirs('dist', exist_ok=True)
    for file in os.listdir('dist'):
        os.remove(os.path.join('dist', file))

def read_file_content(file_path: str, encoding: str = 'utf-8', prefix: str = ' '*10) -> str:
    """Read the content of a file and return it as a string."""
    with open(file_path, 'r', encoding=encoding) as file:
        content = file.read()

    if not prefix:
        return content
        
    new_content = str()
    for line in content.splitlines():
        if not new_content:
            new_content = f'{line}\n'
            continue
        new_content += f'{prefix}{line}\n'
    return new_content.removesuffix('\n')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
