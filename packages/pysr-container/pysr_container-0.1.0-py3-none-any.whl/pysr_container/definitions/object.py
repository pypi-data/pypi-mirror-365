from logging import Logger
from typing import Union, final, Optional
from pysr_abc_container import ContainerInterface
from ..contract import DefinitionInterface
from ..resolvers.object import ObjectResolver


@final
class Object(DefinitionInterface):
    """
    Определение - значение.
    При разрешении возвращает значение как есть.

    Обязательно для конфигурирования контейнера статичными значениями для предотвращения попытки разрешения
    зависимости по типу.
    """

    def __init__(self, object_type: type, init_arguments: dict = None, single_instance: bool = False):
        self.__type = object_type
        self.__init_arguments: Optional[dict] = init_arguments
        self.__single_instance: bool = single_instance
        self.__instance = None

    def resolve(self, container: ContainerInterface, logger: Logger = None):
        if self.__single_instance and self.__instance is not None:
            return self.__instance

        obj = ObjectResolver(container, self.__type, self.__init_arguments).resolve()

        if self.__single_instance:
            self.__instance = obj

        return obj
