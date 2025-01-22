from typing import Optional

class ApiException(Exception):
    """API异常基类"""
    def __init__(self, message: str, code: int = 500, data: Optional[dict] = None):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(message)

class AuthException(ApiException):
    """认证相关异常"""
    def __init__(self, message: str = "认证失败", code: int = 401):
        super().__init__(message=message, code=code)

class PermissionException(ApiException):
    """权限相关异常"""
    def __init__(self, message: str = "权限不足", code: int = 403):
        super().__init__(message=message, code=code)

class NotFoundException(ApiException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在", code: int = 404):
        super().__init__(message=message, code=code)

class ValidationException(ApiException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败", code: int = 400):
        super().__init__(message=message, code=code) 