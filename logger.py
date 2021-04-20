import datetime

LOG_FOLDER = '/logs'

LOG_EXTENSION = '.log'


def create_error_log(path):
    with open(path+'/'+'error.log', 'w') as f:
        pass


def write_log_message_into_file_with_path(client_ip, host_name, path, response_status, content_length, user_agent,
                                          file_full_path, is_error):
    current_date = datetime.date.today().ctime()
    log_message = '[' + current_date + ']' + ' ' + client_ip + ' ' + host_name + ' ' + path + ' ' + response_status \
                  + ' ' + content_length + ' ' + user_agent + '\n'
    if is_error:
        with open('logs/error.log', 'a') as the_file:
            the_file.write(log_message)
    else:
        with open(file_full_path, 'a') as the_file:
            the_file.write(log_message)
