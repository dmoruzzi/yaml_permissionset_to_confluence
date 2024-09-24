from jinja2 import Environment, FileSystemLoader
import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import argparse
import datetime

def make_template():
    return """
<body>

<h1>Overview: {{ permission_set.label }}</h1>
<p>This webpage provides an overview of the configuration of the {{ permission_set.label }} permission set.</p>
{%- if permission_set.label %}
<p><strong>Label:</strong> {{ permission_set.label }}</p>
{%- endif %}
{%- if permission_set.description %}
<p><strong>Description:</strong> {{ permission_set.description }}</p>
{%- endif %}
{%- if permission_set.hasActivationRequired %}
<p><strong>Activation Required:</strong> {{ permission_set.hasActivationRequired }}</p>
{%- endif %}
{%- if permission_set.userLicense %}
<p><strong>User License:</strong> {{ permission_set.userLicense }}</p>
{%- endif %}
{%- if permission_set.sessionTimeout %}
<p><strong>Session Timeout:</strong> {{ permission_set.sessionTimeout }}</p>
{%- endif %}
<p><small>YYYY-MM-DD | #ORG</small></p>
<hr />

{% if permission_set.objectPermissions %}
<h2>Object Permissions</h2>
<p>Defines the permissions granted to users for performing Create, Read, Update, and Delete (CRUD) operations on specific Salesforce objects.</p>

<table>
    <thead>
        <tr>
            <th scope="col">SObject</th>
            <th scope="col">Allow Create</th>
            <th scope="col">Allow Read</th>
            <th scope="col">Allow Edit</th>
            <th scope="col">Allow Delete</th>
            <th scope="col">Modify All Records</th>
            <th scope="col">View All Records</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.objectPermissions is iterable %}
            {%- if permission_set.objectPermissions is mapping %}
                <tr>
                    <td>{{ permission_set.objectPermissions.object }}</td>
                    <td>{{ permission_set.objectPermissions.allowCreate }}</td>
                    <td>{{ permission_set.objectPermissions.allowRead }}</td>
                    <td>{{ permission_set.objectPermissions.allowEdit }}</td>
                    <td>{{ permission_set.objectPermissions.allowDelete }}</td>
                    <td>{{ permission_set.objectPermissions.modifyAllRecords }}</td>
                    <td>{{ permission_set.objectPermissions.viewAllRecords }}</td>
                </tr>
            {%- else %}
                {%- for object_permission in permission_set.objectPermissions %}
                <tr>
                    <td>{{ object_permission.object }}</td>
                    <td>{{ object_permission.allowCreate }}</td>
                    <td>{{ object_permission.allowRead }}</td>
                    <td>{{ object_permission.allowEdit }}</td>
                    <td>{{ object_permission.allowDelete }}</td>
                    <td>{{ object_permission.modifyAllRecords }}</td>
                    <td>{{ object_permission.viewAllRecords }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="7">No object permissions available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.fieldPermissions %}
<h2>Field Permissions</h2>
<p>Specifies the visibility and editability settings for individual fields within Salesforce objects, determining which fields users can view and modify.</p>

<table>
    <thead>
        <tr>
            <th scope="col">SObject</th>
            <th scope="col">Field</th>
            <th scope="col">Readable</th>
            <th scope="col">Updatable</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.fieldPermissions is iterable %}
        {%- if permission_set.fieldPermissions is mapping %}
        {# This means that we have only one field permission. #}
        <tr>
            <td>{{ permission_set.fieldPermissions.field.split('.')[0] if permission_set.fieldPermissions.field is not none else '' }}</td>
            <td>{{ permission_set.fieldPermissions.field.split('.')[1] if permission_set.fieldPermissions.field is not none and permission_set.fieldPermissions.field.split('.')|length > 1 else '' }}</td>
            <td>{{ permission_set.fieldPermissions.readable }}</td>
            <td>{{ permission_set.fieldPermissions.editable }}</td>
        </tr>
        {%- else %}
            {%- for field_permission in permission_set.fieldPermissions %}
            {# This means that we have multiple field permissions. #}
            <tr> 
                <td>{{ field_permission.field.split('.')[0] if field_permission.field is not none else '' }}</td>
                <td>{{ field_permission.field.split('.')[1] if field_permission.field is not none and field_permission.field.split('.')|length > 1 else '' }}</td>
                <td>{{ field_permission.readable }}</td>
                <td>{{ field_permission.editable }}</td>
            </tr>
            {%- endfor %}
        {%- endif %}
        {%- else %}
            <tr>
                <td colspan="4">No field permissions available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.applicationVisibility %}
<h2>Application Visibility</h2>
<p>Establishes which applications users can access and the specific actions they can perform on records within those applications, ensuring appropriate access control.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Application</th>
            <th scope="col">Visibility</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.applicationVisibility is iterable %}
            {%- if permission_set.applicationVisibility is mapping %}
                <tr>
                    <td>{{ permission_set.applicationVisibility.application }}</td>
                    <td>{{ permission_set.applicationVisibility.visibility }}</td>
                </tr>
            {%- else %}
                {%- for application_visibility in permission_set.applicationVisibility %}
                <tr>
                    <td>{{ application_visibility.application }}</td>
                    <td>{{ application_visibility.visibility }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No application visibility available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.tabSettings %}
<h2>Tab Settings</h2>
<p>Tab settings are used to define the visibility of tabs in the permission set.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Tab</th>
            <th scope="col">Visibility</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.tabSettings is iterable %}
            {%- if permission_set.tabSettings is mapping %}
                <tr>
                    <td>{{ permission_set.tabSettings.tab }}</td>
                    <td>{{ permission_set.tabSettings.visibility }}</td>
                </tr>
            {%- else %}
                {%- for tab_setting in permission_set.tabSettings %}
                <tr>
                    <td>{{ tab_setting.tab }}</td>
                    <td>{{ tab_setting.visibility }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No tab settings available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.classAccesses %}
<h2>Apex Class Permissions</h2>
<p>Determines the access level users have to specific Apex classes, influencing their ability to execute class methods and access associated records.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Apex Class</th>
            <th scope="col">Enabled</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.classAccesses is iterable %}
            {%- if permission_set.classAccesses is mapping %}
                <tr>
                    <td>{{ permission_set.classAccesses.apexClass }}</td>
                    <td>{{ permission_set.classAccesses.enabled }}</td>
                </tr>
            {%- else %}
                {%- for apex_class_permission in permission_set.classAccesses %}
                <tr>
                    <td>{{ apex_class_permission.apexClass }}</td>
                    <td>{{ apex_class_permission.enabled }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No apex class permissions available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.apexPagePermissions %}
<h2>Apex Page Permissions</h2>
<p>Specifies the access rights users have to individual Apex pages, impacting their ability to view or interact with custom Visualforce pages.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Apex Page</th>
            <th scope="col">Enabled</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.apexPagePermissions is iterable %}
            {%- if permission_set.apexPagePermissions is mapping %}
                <tr>
                    <td>{{ permission_set.apexPagePermissions.apexPage }}</td>
                    <td>{{ permission_set.apexPagePermissions.enabled }}</td>
                </tr>
            {%- else %}
                {%- for apex_page_permission in permission_set.apexPagePermissions %}
                <tr>
                    <td>{{ apex_page_permission.apexPage }}</td>
                    <td>{{ apex_page_permission.enabled }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No apex page permissions available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.loginIpRanges %}
<h2>Login IP Ranges</h2>
<p>Defines the IP address ranges from which users are permitted to log in, enhancing security by restricting access to trusted networks.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Login IP Range</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.loginIpRanges is iterable %}
            {%- if permission_set.loginIpRanges is mapping %}
                <tr>
                    <td>{{ permission_set.loginIpRanges.loginIpRange }}</td>
                </tr>
            {%- else %}
                {%- for login_ip_range in permission_set.loginIpRanges %}
                <tr>
                    <td>{{ login_ip_range.loginIpRange }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No login IP ranges available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.loginHours %}
<h2>Login Hours</h2>
<p>Establishes the specific hours during which users are allowed to log in, providing control over when users can access the Salesforce environment.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Login Hours</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.loginHours is iterable %}
            {%- if permission_set.loginHours is mapping %}
                <tr>
                    <td>{{ permission_set.loginHours.loginHours }}</td>
                </tr>
            {%- else %}
                {%- for login_hour in permission_set.loginHours %}
                <tr>
                    <td>{{ login_hour.loginHours }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No login hours available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{%- if permission_set.recordTypePermissions %}
<h2>Record Type Permissions</h2>
<p>Specifies the access rights users have to different record types, governing their ability to create, edit, and view records of various types within Salesforce.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Record Type</th>
            <th scope="col">Enabled</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.recordTypePermissions is iterable %}
            {%- if permission_set.recordTypePermissions is mapping %}
                <tr>
                    <td>{{ permission_set.recordTypePermissions.recordType }}</td>
                    <td>{{ permission_set.recordTypePermissions.enabled }}</td>
                </tr>
            {%- else %}
                {%- for record_type_permission in permission_set.recordTypePermissions %}
                <tr>
                    <td>{{ record_type_permission.recordType }}</td>
                    <td>{{ record_type_permission.enabled }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No record type permissions available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{% if permission_set.customPermissions %}
<h2>Custom Permissions</h2>
<p>Defines access to specific custom permissions, allowing for granular control over user actions and record interactions beyond standard settings.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Custom Permission</th>
            <th scope="col">Enabled</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.customPermissions is iterable %}
            {%- if permission_set.customPermissions is mapping %}
                <tr>
                    <td>{{ permission_set.customPermissions.customPermission }}</td>
                    <td>{{ permission_set.customPermissions.enabled }}</td>
                </tr>
            {%- else %}
                {%- for custom_permission in permission_set.customPermissions %}
                <tr>
                    <td>{{ custom_permission.customPermission }}</td>
                    <td>{{ custom_permission.enabled }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No custom permissions available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{%- if permission_set.oauthScopes -%}
<h2>OAuth Scopes</h2>
<p>Specifies the OAuth scopes that users can utilize when logging in, ensuring that only authorized scopes are granted access to the application.</p>

<table>
    <thead>
        <tr>
            <th scope="col">OAuth Scope</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.oauthScopes is iterable %}
            {%- if permission_set.oauthScopes is mapping %}
                <tr>
                    <td>{{ permission_set.oauthScopes.oauthScope }}</td>
                </tr>
            {%- else %}
                {%- for oauth_scope in permission_set.oauthScopes %}
                <tr>
                    <td>{{ oauth_scope.oauthScope }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No OAuth scopes available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}

{%- if permission_set.otherSettings %}
<h2>Other Settings</h2>
<p>Includes various additional settings associated with the permission set that do not fall under standard categories, allowing for further customization of user access and functionality.</p>

<table>
    <thead>
        <tr>
            <th scope="col">Setting</th>
            <th scope="col">Value</th>
        </tr>
    </thead>
    <tbody>
        {%- if permission_set.otherSettings is iterable %}
            {%- if permission_set.otherSettings is mapping %}
                <tr>
                    <td>{{ permission_set.otherSettings.setting }}</td>
                    <td>{{ permission_set.otherSettings.value }}</td>
                </tr>
            {%- else %}
                {%- for other_setting in permission_set.otherSettings %}
                <tr>
                    <td>{{ other_setting.setting }}</td>
                    <td>{{ other_setting.value }}</td>
                </tr>
                {%- endfor %}
            {%- endif %}
        {%- else %}
            <tr>
                <td colspan="2">No other settings available.</td>
            </tr>
        {%- endif %}
    </tbody>
</table>

<hr />
{% endif %}


</body>
"""

def export_html_file(json_file, output_dir, org_name):
    with open(json_file, 'r') as f:
        permission_set = json.load(f)
    
    

    # Create a Jinja2 environment and render the template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.from_string(make_template())
    html_content = template.render(permission_set=permission_set['PermissionSet'])
    timestamp = datetime.datetime.now().strftime('%Y-%b-%d')
    html_content = html_content.replace('YYYY-MM-DD', timestamp)
    html_content = html_content.replace('#ORG', org_name)

    # standardize the true and false values for ease of use
    html_content = html_content.replace("<td>false</td>", "<td>FALSE</td>")
    html_content = html_content.replace("<td>true</td>", "<td><span style='color: #E08738; font-weight: bold'>TRUE</span></td>")

    html_file = os.path.join(output_dir, os.path.basename(json_file).removesuffix('.json') + '.html')
    
    with open(html_file, 'w') as f:
        f.write(html_content)

    logging.info(f"Converted {json_file} to {html_file}")

def process_json_to_html_files(input_dir, output_dir, extension, org_name):
    """Process files with the specified extension in the input directory and save them as HTML in the output directory."""
    logging.basicConfig(level=logging.DEBUG)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.debug(f"Created output directory: {output_dir}")

    # Find files with the given extension in the input directory
    files = [f for f in os.listdir(input_dir) if f.endswith(extension)]
    logging.debug(f"Found {len(files)} files with extension {extension} in {input_dir} - {files}")

    with ThreadPoolExecutor() as executor:
        for file in files:
            json_filename = os.path.join(input_dir, file)

            # Submit each file for parallel processing
            logging.debug(f"Processing {json_filename}")
            executor.submit(export_html_file, json_filename, output_dir, org_name)

    logging.info(f"Converted {len(files)} files to HTML in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert JSON files to HTML tables")
    parser.add_argument('--input_dir', '-i', required=True, help="Directory containing JSON files")
    parser.add_argument('--output_dir', '-o', required=True, help="Directory to save HTML files")
    parser.add_argument('--extension', '-e', default='.json', help="File extension to process (default: .json)")
    parser.add_argument('-a', '--alias', default='PROD', help="Alias of the organization (default: PROD)")

    args = parser.parse_args()

    # Process the files with the specified extension and convert them to HTML
    process_json_to_html_files(args.input_dir, args.output_dir, args.extension, args.alias)
