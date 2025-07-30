from pysr_abc_container import ContainerInterface
from typing import final, get_type_hints

from pysr_container.resolvers.arguments import ArgumentsResolver
from pysr_container.resolvers.resolved.function import Function


@final
class FunctionResolver:

    def __init__(self, container: ContainerInterface, function, arguments):
        self.__container = container
        self.__function = function
        self.__arguments = arguments

    @property
    def typed_arguments(self):
        return get_type_hints(self.__function).copy()

    @property
    def named_arguments(self):
        return self.__arguments

    def resolve(self) -> Function:
        arguments = ArgumentsResolver(self.__container, self.typed_arguments, self.named_arguments).resolve()
        return Function(self.__function, arguments)
