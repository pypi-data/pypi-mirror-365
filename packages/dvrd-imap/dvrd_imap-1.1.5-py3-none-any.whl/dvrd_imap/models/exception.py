class IMAPException(Exception):
    def __init__(self, *args, message=None):
        super().__init__(*args)
        self.message = message
