
def is_host_header_valid(host_header_value, virtual_hosts):
    for x in virtual_hosts.keys():
        for y in virtual_hosts[x]:
            if y[1] in host_header_value:
                return True
    return False
