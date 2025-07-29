from typing import Optional


class APIException(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIConnectionError(APIException):
    def __init__(self, message: str = "Connection failed"):
        super().__init__(message)


class APIAuthenticationError(APIException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class APITimeoutError(APIException):
    def __init__(self, message: str = "Request timeout"):
        super().__init__(message)


class APIValidationError(APIException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400)


class APINotFoundError(APIException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)