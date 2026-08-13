class AppException(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)

class BecaNotFoundException(AppException):
    def __init__(self, detail: str = "Beca no encontrada"):
        super().__init__(detail=detail, status_code=404)

class InvalidFilterException(AppException):
    def __init__(self, detail: str = "Filtro inválido"):
        super().__init__(detail=detail, status_code=400)

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "No autorizado"):
        super().__init__(detail=detail, status_code=401)

class DatabaseUnavailableException(AppException):
    def __init__(self, detail: str = "Servicio de base de datos no disponible"):
        super().__init__(detail=detail, status_code=503)