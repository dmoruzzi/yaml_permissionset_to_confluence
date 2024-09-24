import jinja2
import os
import logging



def main():
    workflow_template = fetch_template(dir="templates", name="workflow.yml.jinja2")
    python_template = fetch_template(dir="templates", name="local_win_python.py")

    # whoami?
    output = os.popen("whoami").read()
    logging.debug(f"Command output: {output}")

    # Template context
    context = dict()
    context["workflow_name"] = 'SF PS Report'
    context["prefix"] = ' '*10
    context["python_version"] = '3.12'  
    context["sf_install"] = True
    context["sf_empty_project"] = [{
        "comment": "Create an empty project in Salesforce",
        "name": "salesforce",
    }]

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

    context["execute_python"] = []
    context["execute_python"].append({
        "name": "XML to JSON",
        "comment": "Convert XML Permissionsets to JSON for table creation",
        "script": "./xml_to_json.py",
        "parameters": "-i ./force-app/main/default/permissionsets -o ./permset"
    })


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
    # prefix with scripts/xml_to_json.py until 'if __name__ == "__main__":' (exclusive)
    with open('scripts/xml_to_json.py', 'r') as f:
        inject_text = f.read().split('if __name__ == "__main__":')
    python_text = inject_text[0] + python_text
    save_dist(output=python_text, file="local_win_python.py")


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
