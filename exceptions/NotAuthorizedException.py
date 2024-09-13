
class NotAuthorizedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __init__(self, message):            
        super().__init__(message)