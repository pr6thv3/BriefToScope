class BriefToScopeError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(BriefToScopeError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class NotFoundError(BriefToScopeError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class AuthError(BriefToScopeError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AIServiceError(BriefToScopeError):
    def __init__(self, message: str = "AI service error"):
        super().__init__(message, status_code=502)


class StorageError(BriefToScopeError):
    def __init__(self, message: str = "Storage error"):
        super().__init__(message, status_code=500)
