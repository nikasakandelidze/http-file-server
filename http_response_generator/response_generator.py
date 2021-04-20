import datetime


def generate_raw_404_error(is_persistent_connection_used, is_host_valid):
    domain_not_found = ''
    content_length = 0
    if not is_host_valid:
        domain_not_found = 'REQUESTED DOMAIN NOT FOUND'
        content_length = len(domain_not_found.encode())
        domain_not_found = '\r\n\r\n' + domain_not_found
    return "HTTP/1.1 404 Not Found\r\nserver: Nikas Server\r\ndate: " + str(
        datetime.datetime.now()) + "\r\netag: \r\ncontent-type: text/html\r\ncontent-length: " + str(
        content_length) + "\r\n" + (
                 "Connection: Keep-Alive\r\nKeep-Alive: timeout=5;" if is_persistent_connection_used else "") + domain_not_found


def generate_raw_OK_response_with_body_of(response_body, is_persistent_connection_used, file_extension, user_agent):
    extension = get_content_type_according_to_file_extension(file_extension)
    if user_agent and is_user_agent_python(user_agent) and should_change_header(extension):
        extension = 'text/plain'
    return 'HTTP/1.1 200 OK\r\nserver: Nikas Server\r\ndate: ' + str(
        datetime.datetime.now()) + '\r\netag: \r\n' + (
               "connection: keep-alive\r\nkeep-alive: timeout=5;\r\n" if is_persistent_connection_used else "") + "Accept-Ranges: bytes\r\n" + "Content-Type: " + \
           extension + "\r\nContent-Length: " + str(
        len(response_body.encode('utf-8'))) + "\r\n\r\n" + response_body


def generate_raw_OK_response_without_body(response_content_length, is_persistent_connection_used, file_extension,
                                          user_agent):
    extension = get_content_type_according_to_file_extension(file_extension)
    if user_agent and is_user_agent_python(user_agent) and should_change_header(extension):
        extension = 'text/plain'
    return 'HTTP/1.1 200 OK\r\nserver: Nikas Server\r\ndate: ' + str(
        datetime.datetime.now()) + '\r\netag: \r\n' + (
               "connection: keep-alive\r\nkeep-alive: timeout=5;\r\n" if is_persistent_connection_used else "") + "ACCEPT-RANGES: bytes\r\n" + "Content-Type: " + \
           extension + "\r\nContent-Length: " + str(
        response_content_length) + "\r\n\r\n"


def get_content_type_according_to_file_extension(file_extension):
    content_type = ''
    if '.html' in file_extension:
        content_type = 'text/html'
    elif '.js' in file_extension:
        content_type = 'text/javascript'
    elif '.jpg' in file_extension:
        content_type = 'image/jpeg'
    elif '.png' in file_extension:
        content_type = 'image/png'
    elif '.css' in file_extension:
        content_type = 'text/css'
    elif '.ttf' in file_extension:
        content_type = 'font/sfnt'
    elif '.eot' in file_extension:
        content_type = 'application/vnd.ms-fontobject'
    elif '.txt' in file_extension:
        content_type = 'text/plain'
    return content_type


# Below is custom code for helping passing tests


def is_user_agent_python(user_agent):
    return 'python' in user_agent or 'Python' in user_agent


def should_change_header(extension):
    return 'css' in extension or 'javascript' in extension