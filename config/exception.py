class BaseDomainException(Exception):

    message = 'Ocorreu um erro de dominio.'
    status_code = 400

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message
        super().__init__(message)
