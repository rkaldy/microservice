from sqlalchemy import Executable


class RetryableQueryError(Exception):
    def __init__(self, stmt: Executable):
        self.stmt = stmt

    def __str__(self) -> str:
        return f"Cause: {self.__cause__}, SQL statement: {self.stmt}"
