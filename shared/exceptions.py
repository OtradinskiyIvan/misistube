class AppBaseError(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class InfrastructureError(AppBaseError):
    def __init__(self, message: str, code: str = "INFRA_ERROR"):
        super().__init__(message, code, status_code=500)

class AuthenticationError(AppBaseError):
    def __init__(self, message: str = "Invalid credentials", code: str = "AUTH_FAILED"):
        super().__init__(message, code, status_code=401)

class ValidationAppError(AppBaseError):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, code, status_code=400)