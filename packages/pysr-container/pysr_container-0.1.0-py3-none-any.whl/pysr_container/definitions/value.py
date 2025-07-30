from typing import final
from pysr_abc_container import ContainerInterface
from ..contract import DefinitionInterface


@final
class Value(DefinitionInterface):
    """
    Определение - значение.
    При разрешении возвращает значение как есть.

    Обязательно для конфигурирования контейнера статичными значениями для предотвращения попытки разрешения
    зависимости по типу.
    """

    def __init__(self, value):
        self.__value = value

    def resolve(self, container: ContainerInterface):
        return self.__value
