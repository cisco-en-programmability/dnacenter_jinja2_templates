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
    This script will deploy a config file to a number of devices based on device family
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

    print('\nThe devices to which the template will be deployed are:', switch_list_reachable)
    print('\nThe unreachable devices to which the template will not be deployed are:', switch_list_unreachable, '\n')

    for switch in switch_list_reachable:
        # deploy the template
        deployment_id = dnac_apis.send_deploy_template_no_params(DEPLOY_TEMPLATE, DEPLOY_PROJECT, switch, dnac_auth)
    
        print('\nTemplate "' + DEPLOY_TEMPLATE + '" started, task id: "' + deployment_id + '"')
        time.sleep(1)  # wait for the deployment task to be created
    
        deployment_status = dnac_apis.check_template_deployment_status(deployment_id, dnac_auth)
        print('Deployment task result for switch: ', switch, ' is: ', deployment_status)

        # optional for manual deployment to test
        # value = input('Input y/n to continue ')
        # if value == 'n':
        #    break

    date_time = str(datetime.datetime.now().replace(microsecond=0))
    print('\n\nEnd of Application "deploy_configs.py" Run: ' + date_time)
    return


if __name__ == "__main__":
    main()
