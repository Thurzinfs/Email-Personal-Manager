from config.exception import BaseDomainException


class TokenExpiredException(BaseDomainException):
    message = 'Token expired'
    status_code = 400
