#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

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
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# This file contains:
# Cisco DNA Center access info


DNAC_IP = 'your_dna_center'
DNAC_URL = 'https://' + DNAC_IP
DNAC_USER = 'username'
DNAC_PASS = 'password'


PROJECT_J2 = 'Cat9k_GS_Prov'
MANAGEMENT_INT_J2 = 'management_interface.j2'
NTP_SERVER_J2 = 'ntp_server.j2'

GS_DEPLOY_PROJECT = 'Cat9k_GS_Prov'
GS_DEPLOY_TEMPLATE = 'gs_prov.j2'
GS_ENABLE_TEMPLATE = 'gs_enable.j2'

DEVICE_NAME = 'PDX-RN'
DEVICE_TYPES = ['Cisco Catalyst38xx stack-able ethernet switch', 'Cisco Catalyst 9300 Switch']
PARAMS = {'interface_number': '101', 'ip_address': '101.100.100.100'}
