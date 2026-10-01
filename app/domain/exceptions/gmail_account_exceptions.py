from config.exception import BaseDomainException


class GmailAccountNotConnectedException(BaseDomainException):
    message = 'Não é possivel renovar o token de uma conta desconectada.'
    status_code = 404


class InvalidOAuthStateException(BaseDomainException):
    message = 'A tentativa de conexão com o gmail expirou ou e invalida.'
    status_code = 400
    