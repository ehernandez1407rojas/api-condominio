# domain/exceptions.py

class RecursoDuplicadoError(Exception):
    """Se lanza cuando un campo único ya existe en la BD."""
    def __init__(self, campo: str, valor=None, mensaje: str | None = None):
        self.campo = campo
        self.valor = valor
        self.mensaje = mensaje or f"Ya existe un registro con {campo}={valor!r}."
        super().__init__(self.mensaje)