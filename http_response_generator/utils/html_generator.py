from os import listdir, getcwd


def generate_html_for_directory(request_path, document_root):
    a = listdir(getcwd() + "/" + document_root + "/" + (request_path if not request_path == '/' else ''))
    return f'''<html><body><ul>{"".join(['<li><a href="' + ('' if request_path == '/' else request_path) + "/" + dir_element + '">' + dir_element + '</a></li>'
                                         for dir_element in a])} </ul></body></html>'''