from config.exception import BaseDomainException


class UserNotFoundException(BaseDomainException):
    message = 'Usuario nao encontrado.'
    status_code = 404


class EmailAlreadyExistsException(BaseDomainException):
    message = "Este e-mail já esta registrado."
    status_code = 409

