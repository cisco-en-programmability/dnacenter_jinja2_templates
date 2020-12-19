
# Cisco DNA Center Jinja2 Configuration Templates APIs


**Cisco Products & Services:**

- Cisco DNA Center and Cisco IOS XE devices managed by Cisco DNA Center

**Tools & Frameworks:**

- Python environment to run the script

**Usage**

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
 
This sample code is for proof of concepts and labs

**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).
