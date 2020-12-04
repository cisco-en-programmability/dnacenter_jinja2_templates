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


import requests
import json
import urllib3
import time
import sys
import os
import logging
import datetime
import dnac_apis

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from requests.auth import HTTPBasicAuth  # for Basic Auth

from config import DNAC_URL, DNAC_PASS, DNAC_USER
from config import PROJECT_J2, MANAGEMENT_INT_TEMPL_J2, NTP_SERVER_J2, DEVICE_NAME, PARAMS

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def main():
    """
    This script will load the file with the name {file_info}
    The file includes the information required to deploy the template. The network device hostname, the Cisco DNA Center
    project name, the configuration template file name.
    The application will:
     - verify if the project exists and create a new project if does not
     - update or upload the configuration template
     - commit the template
     - verify the device hostname is valid
     - deploy the template
     - verify completion and status of the template deployment
    """

    # the local date and time when the code will start execution

    date_time = str(datetime.datetime.now().replace(microsecond=0))

    print('\n\nApplication "dnacenter_jinja2_templates.py" Run Started: ' + date_time)

    # get a Cisco DNA Center auth token
    dnac_auth = dnac_apis.get_dnac_jwt_token(DNAC_AUTH)

    # check if existing project, if not create a new project
    project_id = dnac_apis.create_project(PROJECT_J2, dnac_auth)
    if project_id == 'none':
        # unable to find or create the project
        print('\nUnable to create the project: ', PROJECT_J2)
        return

    # continue with the project id
    print('\nThe project id for the the project with the name "' + PROJECT_J2 + '" is: ' + project_id)

    input('\nEnter any key to continue ')

    # Management IP address configuration
    # create new template and commit if not existing
    # update the existing template and commit if existing

    cli_config_name = MANAGEMENT_INT_TEMPL_J2.split('.')[0]  # select the template name from the template file

    cli_file = open(MANAGEMENT_INT_TEMPL_J2, 'r')  # open file with the template
    cli_config_commands = cli_file.read()  # read the file

    template_param = [
        {
            "parameterName": "interface_number",
            "dataType": "STRING",
            "required": True,
            "order": 1
        },
        {
            "parameterName": "ip_address",
            "dataType": "STRING",
            "required": True,
            "order": 2
        }
    ]

    # upload and commit the template
    dnac_apis.upload_template(cli_config_name, PROJECT_J2, cli_config_commands, template_param, dnac_auth)

    input('\nTemplate created, Enter any key to continue \n')

    # deploy the template
    dnac_apis.send_deploy_template(MANAGEMENT_INT_TEMPL_J2, PROJECT_J2, DEVICE_NAME, PARAMS, dnac_auth)

    date_time = str(datetime.datetime.now().replace(microsecond=0))
    print('\n\nEnd of Application "dnacenter_jinja2_templates.py" Run: ' + date_time)
    return


if __name__ == "__main__":
    main()

