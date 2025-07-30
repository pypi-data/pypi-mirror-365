class InvalidSearchType(Exception):
    def __init__(self, message: str = "Invalid search type."):
        self.message = message
        super().__init__(self.message)
