import re


# Notice: methods with namse starting with '_' are private methods

def get_type_of_raw_http_request(raw_http_request):
    split = raw_http_request.split()
    if not split:
        return "GET"
    return split[0]


def get_path_of_raw_http_request(raw_http_request):
    split = raw_http_request.split()
    if len(split) <= 1:
        return "/"
    return split[1]


def get_headers_of_raw_http_request(raw_http_request):
    splitted_http_request = raw_http_request.splitlines()
    list_of_raw_headers = splitted_http_request[1:]
    list_of_headers = _process_raw_headers_list(list_of_raw_headers)
    return list_of_headers


def get_user_agent_header(raw_http_request):
    for http_request_line in raw_http_request.split('\n'):
        if re.match('User-Agent: .*', http_request_line):
            return http_request_line.split(':')[1].strip()


def is_http_request_persistent(raw_http_request):
    return any(x in raw_http_request for x in ['Connection: Keep-Alive', 'Connection: keep-alive'])


def has_http_request_close_header(raw_http_request):
    return 'Connection: close' in raw_http_request


def get_http_request_host_header(raw_http_request):
    for http_request_line in raw_http_request.split('\n'):
        line_array = http_request_line.split(':')
        if not line_array:
            break
        if 'Host' in line_array[0] or 'host' in line_array[0]:
            return line_array[1]
    return 'None'


def get_value_tuple_for_range_header(raw_http_request, range_low_bound, range_high_bound):
    for http_request_line in raw_http_request.split('\n'):
        if re.match('Range: bytes=([0-9])*-([0-9])*', http_request_line):
            key, value = http_request_line.split(':')
            string_of_actual_range = value.split('=')[1].rstrip()
            index_of_slash_char = string_of_actual_range.index('-')
            if len(string_of_actual_range) - 1 > index_of_slash_char > 0:
                return int(string_of_actual_range[0:index_of_slash_char]), \
                       int(string_of_actual_range[index_of_slash_char + 1:])
            elif index_of_slash_char == 0:
                return range_low_bound, int(string_of_actual_range[index_of_slash_char + 1:])
            else:
                return int(string_of_actual_range[0:index_of_slash_char]), range_high_bound
    return range_low_bound, range_high_bound


def _process_raw_headers_list(list_of_raw_headers):
    list_of_headers = list()
    for header in list_of_raw_headers:
        if header == '':
            break
        else:
            list_of_headers.append(_process_raw_header(header))
    return list_of_headers


def _process_raw_header(raw_header):
    splitted_header = raw_header.split(":")
    return {splitted_header[0]: splitted_header[1]}


# Custom exception for incorrect http string input
class IncorrectHttpRequestException(Exception):
    pass
