from typing import Union, Any, final
from pysr_abc_container import ContainerInterface
from .contract import DefinitionInterface
from .exceptions import NotFoundError
from .stack import Stack


@final
class Container(ContainerInterface):

    __definitions: dict[Union[str, type], Any] = {}

    def __init__(self, definitions: dict):
        if ContainerInterface not in definitions:
            definitions[ContainerInterface] = self
        self.__definitions = definitions
        self.__stack = Stack()

    def has(self, name: Union[str, type]) -> bool:
        return name in self.__definitions

    def get(self, name: Union[str, type]) -> Any:
        self.__stack.push(name)
        if not self.has(name):
            raise NotFoundError(f'Entry "{name}" not found')
        item = self.__definitions[name]
        if isinstance(item, DefinitionInterface):
            item = item.resolve(self)
        self.__stack.mark_as_resolved(name)
        return item
