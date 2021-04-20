import json


def get_virtual_host_info_dict(file_full_path):
    with open(file_full_path) as json_file:
        data = json.loads(json_file.read())
        return data['server']


def get_first_virtual_host_info_dict(file_full_path):
    return get_virtual_host_info_dict(file_full_path)[0]
