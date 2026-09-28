from config.exception import BaseDomainException


class TokenExpiredException(BaseDomainException):
    message = 'Token expired'
    status_code = 400


class InvalidTokenException(BaseDomainException):
    message = 'invalid token'
    status_code = 401
