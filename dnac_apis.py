#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Cisco DNA Center Command Runner

Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Gabriel Zapodeanu TME, ENB"
__email__ = "gzapodea@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import requests
import json
import time
import urllib3
import utils

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from requests.auth import HTTPBasicAuth  # for Basic Auth

from config import DNAC_URL, DNAC_PASS, DNAC_USER


urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data: data to pretty print
    :return:
    """
    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_dnac_jwt_token(dnac_auth):
    """
    Create the authorization token required to access DNA C
    Call to DNA C - /api/system/v1/auth/login
    :param dnac_auth - DNA C Basic Auth string
    :return: DNA C JWT token
    """
    url = DNAC_URL + '/dna/system/api/v1/auth/token'
    header = {'content-type': 'application/json'}
    response = requests.post(url, auth=dnac_auth, headers=header, verify=False)
    dnac_jwt_token = response.json()['Token']
    return dnac_jwt_token


def get_all_device_info(dnac_jwt_token):
    """
    The function will return all network devices info
    :param dnac_jwt_token: Cisco DNA Center token
    :return: DNA C device inventory info
    """
    url = DNAC_URL + '/dna/intent/api/v1/network-device'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    all_device_response = requests.get(url, headers=header, verify=False)
    all_device_info = all_device_response.json()
    return all_device_info['response']


def get_device_info(device_id, dnac_jwt_token):
    """
    This function will retrieve all the information for the device with the DNA C device id
    :param device_id: DNA C device_id
    :param dnac_jwt_token: Cisco DNA Center token
    :return: device info
    """
    url = DNAC_URL + '/dna/intent/api/v1/network-device?id=' + device_id
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    device_response = requests.get(url, headers=header, verify=False)
    device_info = device_response.json()
    return device_info['response'][0]


def get_project_id(project_name, dnac_jwt_token):
    """
    This function will retrieve the CLI templates project id for the project with the name {project_name}
    :param project_name: CLI project name
    :param dnac_jwt_token: Cisco DNA Center token
    :return: project id
    """
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/project?name=' + project_name
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    project_json = response.json()
    project_id = project_json[0]['id']
    return project_id


def create_project(project_name, dnac_jwt_token):
    """
    This function will create a new project with the name {project_name}.
    - if the project exists, return the project id
    - if the project does not exist it will create a new project, waiting for the task to be completed
     and return the project id
    :param project_name: project name
    :param dnac_jwt_token: Cisco DNA Center token
    :return: project id, or none if creating a new project fails
    """

    # check if project exists
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/project?name=' + project_name
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    project_json = response.json()
    # if project does not exist, project_json value is []. We need to create the project
    if project_json == []:
        # project does not exist
        payload = {'name': project_name}
        url = DNAC_URL + '/dna/intent/api/v1/template-programmer/project'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
        task_json = response.json()
        task_info = task_json['response']
        task_id = task_info['taskId']
        task_result = check_task_id_status(task_id, dnac_jwt_token)
        project_id = task_result['data']
    else:
        # project exists
        project_id = project_json[0]['id']
    return project_id


def delete_project(project_name, dnac_jwt_token):
    """
    This function will retrieve the CLI templates project id for the project with the name {project_name}
    :param project_name: CLI project name
    :param dnac_jwt_token: Cisco DNA Center token
    :return: project id
    """
    project_id = get_project_id(project_name, dnac_jwt_token)
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/project/' + project_id
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.delete(url, headers=header, verify=False)


def get_project_info(project_name, dnac_jwt_token):
    """
    This function will retrieve all templates associated with the project with the name {project_name}
    :param project_name: project name
    :param dnac_jwt_token: Cisco DNA Center token
    :return: list of all templates, including names and ids
    """
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/project?name=' + project_name
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    project_json = response.json()
    template_list = project_json[0]['templates']
    return template_list


def create_commit_template(template_name, project_name, cli_template, template_param, dnac_jwt_token):
    """
    This function will create and commit a CLI template, under the project with the name {project_name}, with the the text content
    {cli_template}
    :param template_name: CLI template name
    :param project_name: Project name
    :param cli_template: CLI template text content
    :param template_param: the template parameters, as a an array, or none
    :param dnac_jwt_token: Cisco DNA Center token
    :return:
    """
    project_id = get_project_id(project_name, dnac_jwt_token)

    # prepare the template param to sent to DNA C
    payload = {
            "name": template_name,
            "tags": [],
            "author": "demotme",
            "deviceTypes": [
                {
                    "productFamily": "Routers"
                },
                {
                    "productFamily": "Switches and Hubs"
                }
            ],
            "softwareType": "IOS-XE",
            "softwareVariant": "XE",
            "softwareVersion": "",
            "templateContent": cli_template,
            "rollbackTemplateContent": "",
            "rollbackTemplateParams": [],
            "parentTemplateId": project_id,
            "language": "JINJA",
            "templateParams": template_param
        }

    # check and delete older versions of the template
    template_id = get_template_id(template_name, project_name, dnac_jwt_token)
    if template_id:
        delete_template(template_name, project_name, dnac_jwt_token)

    # create the new template
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/project/' + project_id + '/template'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)

    # get the template id
    template_id = get_template_id(template_name, project_name, dnac_jwt_token)

    # commit template
    commit_template(template_id, 'committed by Python script', dnac_jwt_token)


def commit_template(template_id, comments, dnac_jwt_token):
    """
    This function will commit the template with the template id {template_id}
    :param template_id: template id
    :param comments: text with comments
    :param dnac_jwt_token: Cisco DNA Center token
    :return:
    """
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/template/version'
    payload = {
            "templateId": template_id,
            "comments": comments
        }
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    return response


def update_commit_template(template_name, project_name, cli_template, template_param, dnac_jwt_token):
    """
    This function will update an existing template
    :param template_name: template name
    :param project_name: project name
    :param cli_template: CLI template text content
    :param template_param: the template parameters, or none
    :param dnac_jwt_token: Cisco DNA Center token
    :return:
    """
    # get the project id
    project_id = get_project_id(project_name, dnac_jwt_token)

    # get the template id
    template_id = get_template_id(template_name, project_name, dnac_jwt_token)
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/template'

    # prepare the template param to sent to DNA C
    payload = {
        "name": template_name,
        "description": "Remote router configuration",
        "tags": [],
        "id": template_id,
        "author": "admin",
        "deviceTypes": [
            {
                "productFamily": "Routers"
            },
            {
                "productFamily": "Switches and Hubs"
            }
        ],
        "softwareType": "IOS-XE",
        "softwareVariant": "XE",
        "softwareVersion": "",
        "templateContent": cli_template,
        "rollbackTemplateContent": "",
        "templateParams": template_param,
        "rollbackTemplateParams": [],
        "parentTemplateId": project_id
    }
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.put(url, data=json.dumps(payload), headers=header, verify=False)
    print(response.text)
    time.sleep(2)
    # commit template
    response = commit_template(template_id, 'committed by Python script', dnac_jwt_token)
    print(response.text)


def upload_template(template_name, project_name, cli_template, template_param, dnac_jwt_token):
    """
    This function will create, or will update an existing template, and deploy the new template
    :param template_name: template name
    :param project_name: project name
    :param cli_template: CLI template text content
    :param template_param: the template parameters, or none
    :param dnac_jwt_token: Cisco DNA Center token
    :return:
    """
    template_id = get_template_id(template_name, project_name, dnac_jwt_token)
    if template_id:
        create_commit_template(template_name, project_name, cli_template, template_param, dnac_jwt_token)
    else:
        create_commit_template(template_name, project_name, cli_template, template_param, dnac_jwt_token)


def delete_template(template_name, project_name, dnac_jwt_token):
    """
    This function will delete the template with the name {template_name}
    :param template_name: template name
    :param project_name: Project name
    :param dnac_jwt_token: Cisco DNA Center token
    :return:
    """
    template_id = get_template_id(template_name, project_name, dnac_jwt_token)
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/template/' + template_id
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.delete(url, headers=header, verify=False)


def get_all_template_info(dnac_jwt_token):
    """
    This function will return the info for all CLI templates existing on DNA C, including all their versions
    :param dnac_jwt_token: Cisco DNA Center token
    :return: all info for all templates
    """
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/template'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    all_template_list = response.json()
    return all_template_list


def get_template_name_info(template_name, project_name, dnac_jwt_token):
    """
    This function will return the info for the CLI template with the name {template_name}
    :param template_name: template name
    :param project_name: Project name
    :param dnac_jwt_token: Cisco DNA Center token
    :return: all info for all templates
    """
    template_id = get_template_id(template_name, project_name, dnac_jwt_token)
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/template/' + template_id
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    template_json = response.json()
    return template_json


def get_template_id(template_name, project_name, dnac_jwt_token):
    """
    This function will return the template id for the DNA C template with the name {template_name},
    part of the project with the name {project_name}
    :param template_name: name of the template
    :param project_name: Project name
    :param dnac_jwt_token: Cisco DNA Center token
    :return: DNA C template id
    """
    template_info = get_project_info(project_name, dnac_jwt_token)
    try:
        template_id = template_info[0]['id']

    except:
        template_id = None
    return template_id


def send_deploy_template(template_name, project_name, device_name, parameters, dnac_jwt_token):
    """
    This function will deploy the template with the name {template_name} to the network device with the name
    {device_name}
    :param template_name: template name
    :param project_name: project name
    :param device_name: device hostname
    :param parameters: template parameters
    :param dnac_jwt_token: Cisco DNA Center token
    :return: the deployment task id
    """
    template_id = get_template_id(template_name, project_name, dnac_jwt_token)
    payload = {
            "templateId": template_id,
            "forcePushTemplate": True,
            "targetInfo": [
                {
                    "id": device_name,
                    "type": "MANAGED_DEVICE_HOSTNAME",
                    "params": parameters
                }
            ]
        }
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/template/deploy'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    deployment = requests.post(url, headers=header, data=json.dumps(payload), verify=False)
    deployment_json = deployment.json()
    pprint(deployment_json)
    depl_task_id = deployment_json["deploymentId"].split(' ')[-1]
    return depl_task_id


def check_template_deployment_status(depl_task_id, dnac_jwt_token):
    """
    This function will check the result for the deployment of the CLI template with the id {depl_task_id}
    :param depl_task_id: template deployment id
    :param dnac_jwt_token: Cisco DNA Center token
    :return: status - {SUCCESS} or {FAILURE}
    """
    url = DNAC_URL + '/dna/intent/api/v1/template-programmer/template/deploy/status/' + depl_task_id
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    deployment_status = response_json["status"]
    return deployment_status



def check_task_id_status(task_id, dnac_jwt_token):
    """
    This function will check the status of the task with the id {task_id}
    :param task_id: task id
    :param dnac_jwt_token: Cisco DNA Center token
    :return: status - {SUCCESS} or {FAILURE}, and the task status message
    """
    # loop until the task is completed, check status every second
    task_result = ''

    while task_result == '':
        time.sleep(1)
        url = DNAC_URL + '/dna/intent/api/v1/task/' + task_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        task_response = requests.get(url, headers=header, verify=False)
        task_json = task_response.json()
        task_status = task_json['response']
        print(task_status)
        if 'endTime' in task_status.keys():
            return task_status


def check_task_id_output(task_id, dnac_jwt_token):
    """
    This function will check the status of the task with the id {task_id}.
    Loop one seconds increments until task is completed.
    :param task_id: task id
    :param dnac_jwt_token: Cisco DNA Center token
    :return: status - {SUCCESS} or {FAILURE}
    """
    url = DNAC_URL + '/dna/intent/api/v1/task/' + task_id
    header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
    completed = 'no'
    while completed == 'no':
        try:
            task_response = requests.get(url, headers=header, verify=False)
            task_json = task_response.json()
            task_output = task_json['response']
            # check if file id available in output
            file_info = json.loads(task_output['progress'])
            completed = 'yes'
        finally:
            time.sleep(1)
    return task_output

