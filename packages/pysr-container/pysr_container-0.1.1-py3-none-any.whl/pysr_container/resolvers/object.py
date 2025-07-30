from logging import Logger
from typing import final
from pysr_abc_container import ContainerInterface

from ..exceptions import ConstructorError
from ..resolvers.function import FunctionResolver


@final
class ObjectResolver:

    def __init__(self, container: ContainerInterface, object_type: type, init_args: dict = None):
        self.__container = container
        self.__type = object_type
        self.__init_args = init_args

    def get_constructor_resolver(self) -> FunctionResolver:
        return FunctionResolver(self.__container, self.__type.__init__, self.__init_args)

    def resolve(self) -> object:
        constructor = self.get_constructor_resolver().resolve()
        try:
            obj = self.__type(**constructor.arguments)
        except Exception as e:
            raise ConstructorError(e)

        return obj
