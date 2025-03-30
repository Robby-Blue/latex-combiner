class ParserError(Exception):
    def __init__(self, error_message, *args):
        self.error_message = error_message
        super().__init__(*args)