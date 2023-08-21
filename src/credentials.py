import re
import json
import os


def get_active_credentials():
    home_directory = os.path.expanduser('~')
    credentials_path = os.path.join(home_directory, '.aws', 'credentials')

    with open(credentials_path, 'r') as credentials_file:
        data = credentials_file.read()

    pattern = r'\[(.*?)\]'
    matches = re.findall(pattern, data)

    credentials = []

    for match in matches:
        credentials.append(match)

    return credentials
