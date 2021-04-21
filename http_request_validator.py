
def is_host_header_valid(host_header_value, virtual_hosts):
    for virutal_host_key in virtual_hosts.keys():
        for vhost_tuple in virtual_hosts[virutal_host_key]:
            vhost_tuple_ = vhost_tuple[1]
            header_value = './statics/' + host_header_value.strip()
            value = vhost_tuple_ == header_value
            tuple_ = header_value == vhost_tuple_
            if value or tuple_:
                return True
    return False
