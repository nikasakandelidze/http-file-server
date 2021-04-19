class RequestHandlerMessage:
    def __init__(self):
        self.message = {}

    def add_element_into_message(self, key_value_tuple):
        self.message[key_value_tuple[0]] = key_value_tuple[1]

    def get_message(self):
        return self.message
