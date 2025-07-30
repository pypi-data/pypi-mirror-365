from pysr_abc_container import ContainerErrorInterface, NotFoundErrorInterface


class ContainerError(Exception, ContainerErrorInterface):
    """
    Исключение возникает, если произошла ошибка во время разрешения зависимостей.
    """
    def __init__(self, e: Exception):
        self.__origin = e
        super().__init__(str(e))

    @property
    def origin(self) -> Exception:
        return self.__origin


class NotFoundError(Exception, NotFoundErrorInterface):
    """
    Исключение возникает, если в контейнере нет записи с запрошенным идентификатором.
    """
    pass


class ConstructorError(ContainerError):
    pass


class CircularDependencyError(Exception, ContainerErrorInterface): ...