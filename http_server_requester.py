import os
from socket import *
from threading import Thread

import logger
from http_request_parser import is_http_request_persistent, has_http_request_close_header, get_http_request_host_header, \
    get_path_of_raw_http_request, get_user_agent_header
from http_request_validator import *

__BACKLOG = 1024
__SOCKET_RECV_SIZE = 2048
__TIMEOUT = 5

# Key: port, Value:[ (vhost, documentroot) ]
virtual_hosts = {}


def start_receiving_connections(virtual_servers, process_request_callback):
    for virtual_host in virtual_servers:
        _port = virtual_host['port']
        vhost_ = virtual_host['vhost']
        documentroot_ = virtual_host['documentroot']
        # logger.create_log_for_vhost(vhost_)
        vhost_documentroot_tuple = (vhost_, documentroot_)
        if _port in virtual_hosts.keys():
            virtual_hosts[_port].append(vhost_documentroot_tuple)
        else:
            server_socket = socket(AF_INET, SOCK_STREAM)
            server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            server_socket.bind((virtual_host['ip'], _port))
            server_socket.listen(__BACKLOG)
            empty_list = list()
            empty_list.append(vhost_documentroot_tuple)
            virtual_hosts[_port] = empty_list
            vhost_server_thread = Thread(target=serve_vhost, args=(_port, process_request_callback, server_socket))
            vhost_server_thread.start()


def serve_vhost(_port, process_request_callback, server_socket):
    while True:
        _socket, client_address = server_socket.accept()
        new_client_thread = Thread(target=_serve_client, args=(
            _socket, _port, process_request_callback, client_address))
        new_client_thread.start()


def _serve_client(_socket, _port, process_request_callback, client_address):
    raw_client_input = _socket.recv(__SOCKET_RECV_SIZE).decode()
    is_connection_persistent = is_http_request_persistent(raw_client_input)
    request_host_header = get_http_request_host_header(raw_client_input)
    document_root = _get_document_root_for_vhost(_port, request_host_header)
    is_host_valid = is_host_header_valid(request_host_header, virtual_hosts)
    if is_connection_persistent:
        _serve_persistent_connection(_socket, document_root, process_request_callback, raw_client_input, client_address,
                                     is_host_valid)
    else:
        _serve_nonpersistent_connection(_socket, document_root, process_request_callback, raw_client_input,
                                        client_address, is_host_valid)


def _serve_persistent_connection(_socket, document_root, process_request_callback, raw_client_input, client_address,
                                 is_host_valid):
    should_close_connection = False
    log_file_full_path = os.getcwd() + '/logs' + '/' + document_root + '.log'
    try:
        _socket.settimeout(__TIMEOUT)
        while True:
            if has_http_request_close_header(raw_client_input):
                should_close_connection = True
            process_request_callback(raw_client_input, document_root, True,
                                     lambda response_bytes: _socket.sendall(response_bytes),
                                     get_lambda_for_logging(raw_client_input, client_address, log_file_full_path),
                                     is_host_valid)
            if should_close_connection:
                raise Exception('Closing connection according to Connection: Close header')
            raw_client_input = _socket.recv(__SOCKET_RECV_SIZE).decode()
    finally:
        _socket.close()


def _serve_nonpersistent_connection(_socket, document_root, process_request_callback, raw_client_input, client_address,
                                    is_host_valid):
    log_file_full_path = os.getcwd() + '/logs' + '/' + document_root + '.log'
    try:
        process_request_callback(raw_client_input, document_root, False,
                                 lambda response_bytes: _socket.sendall(response_bytes),
                                 get_lambda_for_logging(raw_client_input, client_address, log_file_full_path),
                                 is_host_valid)
    finally:
        _socket.close()


def _get_document_root_for_vhost(_port, host_header_value):
    document_root = 'None'
    if not is_host_header_valid(host_header_value, virtual_hosts):
        return document_root
    list_of_vhosts_on_port = virtual_hosts[_port]
    for vhost in list_of_vhosts_on_port:
        if vhost[0] in host_header_value:
            document_root = vhost[1]
    return document_root


def get_lambda_for_logging(raw_client_input, client_address, file_full_path):
    host = get_http_request_host_header(raw_client_input)
    path = get_path_of_raw_http_request(raw_client_input)
    user_agent = get_user_agent_header(raw_client_input)
    return lambda response_status, content_length, is_error: logger.write_log_message_into_file_with_path(
        '127.0.0.1' if not client_address[0] else client_address[0], host,
        path, response_status,
        content_length,
        user_agent,
        file_full_path, is_error)
