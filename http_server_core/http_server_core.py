from os import path

from request_handler.request_handler import *
from request_handler.http_request_parser.http_request_parser import *
from http_response_generator.response_generator import *
from http_response_generator.utils.html_generator import *


def process_http_request_callback(raw_http_request, document_root,
                                  is_persistent_connection_used, send_response_bytes_callback, log_message_callback,
                                  is_host_valid):
    request_type = get_metohd_type_of_raw_http_request(raw_http_request)
    if request_type == 'GET':
        _serve_get_request(raw_http_request, document_root,
                           is_persistent_connection_used, send_response_bytes_callback, log_message_callback,
                           is_host_valid)
    elif request_type == 'HEAD':
        _serve_head_request(raw_http_request, document_root,
                            is_persistent_connection_used, send_response_bytes_callback, is_host_valid)
    else:
        send_response_bytes_callback("Bad HTTP method".encode())


def is_http_connection_persistent_callback(raw_http_request):
    return is_raw_http_request_persistent(raw_http_request)


def has_http_request_connection_close_header_callback(raw_http_request):
    return has_http_request_close_header(raw_http_request)


def _serve_get_request(raw_http_request, document_root, is_persistent_connection_used, send_response_bytes,
                       log_message_callback, is_host_valid):
    request_path = (get_path_of_raw_http_request(raw_http_request)).replace('%20', " ")
    full_path = getcwd() + "/" + document_root + "/" + request_path
    if not path.exists(full_path):
        response = generate_raw_404_error(is_persistent_connection_used, is_host_valid)
        send_response_bytes(response.encode())
        content_length = '0' if is_host_valid else '26'
        log_message_callback('404', content_length, True)
    elif path.isdir(full_path):
        generated_html_file = generate_html_for_directory(request_path, document_root)
        response_body = _modify_response_body_with_range_headers(generated_html_file, raw_http_request)
        response = generate_raw_OK_response_with_body_of(response_body,
                                                         is_persistent_connection_used, '.html',
                                                         get_user_agent_header_of_raw_http_request(raw_http_request))
        send_response_bytes(response.encode())
        log_message_callback('200', str(len(response_body.encode('utf-8'))), False)
    elif path.isfile(full_path):
        file_extension = path.splitext(full_path)[1]
        with open(full_path, 'rb') as file:
            if is_file_image(full_path) or is_file_font(full_path):
                file_content = file.read()
                file_content = _modify_response_body_with_range_headers(file_content, raw_http_request)
                head_response = generate_raw_OK_response_without_body(len(file_content), is_persistent_connection_used,
                                                                      file_extension,
                                                                      get_user_agent_header_of_raw_http_request(
                                                                          raw_http_request))
                send_response_bytes(head_response.encode() + file_content)
                log_message_callback('200', str(len(file_content)), False)
            else:
                file_content = file.read().decode()
                res = _modify_response_body_with_range_headers(file_content, raw_http_request)
                response = generate_raw_OK_response_with_body_of(res, is_persistent_connection_used,
                                                                 file_extension,
                                                                 get_user_agent_header_of_raw_http_request(
                                                                     raw_http_request))
                send_response_bytes(response.encode())
                log_message_callback('200', str(len(res.encode('utf-8'))), False)


def _serve_head_request(raw_http_request, document_root, is_persistent_connection_used, send_response_bytes,
                        is_host_valid):
    request_path = (get_path_of_raw_http_request(raw_http_request)).replace('%20', " ")

    # is host also present in "path" part?
    # or host is always specified via Host header and path always has path in it like in the book?
    full_path = getcwd() + "/" + document_root + "/" + request_path

    if not path.exists(full_path):
        response = generate_raw_404_error(is_persistent_connection_used, is_host_valid)
        send_response_bytes(response.encode())
    elif path.isdir(full_path):
        response = generate_raw_OK_response_without_body(generate_html_for_directory(request_path, document_root),
                                                         is_persistent_connection_used, '.html',
                                                         get_user_agent_header_of_raw_http_request(raw_http_request))
        send_response_bytes(response.encode())
    elif path.isfile(full_path):
        file_extension = path.splitext(full_path)[1]
        content_size = path.getsize(full_path)
        response = generate_raw_OK_response_without_body(content_size, is_persistent_connection_used, file_extension,
                                                         get_user_agent_header_of_raw_http_request(raw_http_request))
        send_response_bytes(response.encode())


def _modify_response_body_with_range_headers(response_body, raw_http_request):
    lower, upper = get_tuple_of_raw_http_request_range_header(raw_http_request, 0, len(response_body))
    return response_body[lower:upper + 1]


def is_file_image(file_full_path):
    file_extension = path.splitext(file_full_path)[1]
    return file_extension in ['.jpg', '.png', '.jpeg']


def is_file_font(file_full_path):
    file_extension = path.splitext(file_full_path)[1]
    return file_extension in ['.ttf', '.eot']
