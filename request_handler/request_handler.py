# Open server socket, listen, take input http requests, parse them and send constructed message to server Core for
# Invocation of further logic depdendant on message created

import os
from socket import *
from threading import Thread

from .http_request_parser import http_request_parser
from .http_request_validator import http_request_validator

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
    is_connection_persistent = http_request_parser.is_raw_http_request_persistent(raw_client_input)
    request_host_header = http_request_parser.get_host_header_of_raw_http_request(raw_client_input)
    document_root = _get_document_root_for_vhost(_port, request_host_header)
    is_host_valid = http_request_validator.is_host_header_valid(request_host_header)
    if is_connection_persistent:
        _serve_persistent_connection(_socket, document_root, process_request_callback, raw_client_input, client_address,
                                     is_host_valid)
    else:
        _serve_nonpersistent_connection(_socket, document_root, process_request_callback, raw_client_input,
                                        client_address, is_host_valid)


def _serve_persistent_connection(_socket, document_root, process_request_callback, raw_client_input, client_address,
                                 is_host_valid):
    should_close_connection = False
    try:
        _socket.settimeout(__TIMEOUT)
        while True:
            if http_request_parser.has_http_request_close_header(raw_client_input):
                should_close_connection = True
            process_request_callback(raw_client_input, document_root, True,
                                     lambda response_bytes: _socket.sendall(response_bytes),
                                     is_host_valid)
            if should_close_connection:
                raise Exception('Closing connection according to Connection: Close header')
            raw_client_input = _socket.recv(__SOCKET_RECV_SIZE).decode()
    finally:
        _socket.close()


def _serve_nonpersistent_connection(_socket, document_root, process_request_callback, raw_client_input, client_address,
                                    is_host_valid):
    try:
        process_request_callback(raw_client_input, document_root, False,
                                 lambda response_bytes: _socket.sendall(response_bytes), is_host_valid)
    finally:
        _socket.close()


def _get_document_root_for_vhost(_port, host_header_value):
    document_root = 'None'
    if not http_request_validator.is_host_header_valid(host_header_value):
        return document_root
    list_of_vhosts_on_port = virtual_hosts[_port]
    for vhost in list_of_vhosts_on_port:
        if vhost[0] in host_header_value:
            document_root = vhost[1]
    return document_root
