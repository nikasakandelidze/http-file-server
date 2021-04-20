from server_configuration_parser import *
from http_server_requester import *
from http_server_core import *


# Test for configuration parser
def main():
    virtual_host_config = get_virtual_host_info_dict('config.json')
    start_receiving_connections(virtual_host_config, process_http_request_callback)


if __name__ == '__main__':
    main()
