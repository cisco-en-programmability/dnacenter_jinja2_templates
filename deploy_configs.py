#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Cisco DNA Center Jinja2 Configuration Templates

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

import datetime
import time
import json
import csv

import urllib3
from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

import dnac_apis
from config import DNAC_PASS, DNAC_USER
from config import DEPLOY_PROJECT, DEPLOY_TEMPLATE, DEVICE_TYPES
urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """
    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def main():
    """
    This script will deploy a config file to a number of devices based on device family.
    The device family is defined by a list "DEVICE_TYPES"
    It will collect all the devices that match the device types, identify those that are reachable, and those that are
    not reachable.
    The script will deploy the configuration template to each reachable device.
    There are some optional commands included that will allow to test the template deployment to a small number of
    devices first.
    """

    # the local date and time when the code will start execution

    date_time = str(datetime.datetime.now().replace(microsecond=0))

    print('\n\nApplication "deploy_configs.py" Run Started: ' + date_time)

    # get a Cisco DNA Center auth token
    dnac_auth = dnac_apis.get_dnac_jwt_token(DNAC_AUTH)

    # verify if existing template in the project
    template_id = dnac_apis.get_template_id(DEPLOY_TEMPLATE, DEPLOY_PROJECT, dnac_auth)

    print('\nThe template "' + DEPLOY_TEMPLATE + '" id is: ', template_id)

    # find all devices managed by Cisco DNA C, that are "switches and hubs"
    device_list = dnac_apis.get_all_device_list(500, dnac_auth)

    # create the switches list
    switch_list_reachable = []
    switch_list_unreachable = []

    # identify all devices that match the device type
    for device in device_list:
        device_type = device['type']
        if device_type in DEVICE_TYPES:
            hostname = device['hostname']
            if device['reachabilityStatus'] == 'Reachable':
                switch_list_reachable.append(hostname)
            else:
                switch_list_unreachable.append(hostname)

    print('\nThe unreachable devices to which the template will not be deployed are:', switch_list_unreachable, '\n')
    print('\nThe devices to which the template will be deployed are:', switch_list_reachable)
    total_number_devices = len(switch_list_reachable)
    print('\nThe number of devices to deploy the template to is: ', total_number_devices)

    # we will configure a number of devices equal with "device_count" starting with the device from the list
    # identified with "first_record"

    first_record = int(input('\nWhat is the device index you want to start with ? (integer between 0 and ' + str(
        total_number_devices) + ')  '))
    device_count = int(input('How many devices do you want to configure ?  '))
    if device_count + first_record >= total_number_devices:
        device_count = total_number_devices - first_record
        print('Changed the number of the devices to maximum allowed: ', device_count)

    device_index = first_record

    # create a list with the structure [[device hostname, deployment status},...]
    deployment_report = []

    for switch in switch_list_reachable[first_record:first_record+device_count]:
        # deploy the template

        # get a Cisco DNA Center auth token, required for mass device configs, script running will take longer than
        # 60 min.
        dnac_auth = dnac_apis.get_dnac_jwt_token(DNAC_AUTH)

        deployment_id = dnac_apis.send_deploy_template_no_params(DEPLOY_TEMPLATE, DEPLOY_PROJECT, switch, dnac_auth)
    
        print('\nTemplate "' + DEPLOY_TEMPLATE + '" started, task id: "' + deployment_id + '"')
        time.sleep(5)  # wait for the deployment task to be created
    
        deployment_status = dnac_apis.check_template_deployment_status(deployment_id, dnac_auth)
        print('Deployment task result for switch: ', switch, ' is: ', deployment_status, ', device index: ',
              device_index)
        device_index += 1

        deployment_report.append([switch, deployment_id, deployment_status])

        # optional for manual deployment to test
        # value = input('Input y/n to continue ')
        # if value == 'n':
        #    break

    print('\nThe deployment report:\n')
    pprint(deployment_report)

    # save information to file
    output_file = open('deployment_report.csv', 'w', newline='')
    output_writer = csv.writer(output_file)

    # loop through all devices and deployment status to collect the information needed in the report
    for device in deployment_report:
        device_info = [device[0], device[1], device[2]]
        output_writer.writerow(device_info)
    output_file.close()
    print('\n\nFile deployment_report.csv" saved')

    date_time = str(datetime.datetime.now().replace(microsecond=0))
    print('\n\nEnd of Application "deploy_configs.py" Run: ' + date_time)
    return


if __name__ == "__main__":
    main()
