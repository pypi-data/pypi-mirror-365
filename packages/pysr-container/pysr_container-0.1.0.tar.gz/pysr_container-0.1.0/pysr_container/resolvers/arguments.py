from pysr_abc_container import ContainerInterface
from typing import final


@final
class ArgumentsResolver:

    def __init__(self, container: ContainerInterface, typed: dict = None, named: dict = None):
        self.__container = container
        self.__typed = typed
        self.__named = named

    def resolve(self) -> dict:
        resolved = {}
        if self.__named is not None:
            resolved.update(self.__named)
        if self.__typed is not None:
            resolved.update(self.__resolve_by_type(self.__typed))
        return resolved


    def __resolve_by_type(self, source: dict) -> dict:
        resolved = {}
        for name, type_name in source.items():
            if self.__container.has(type_name):
                resolved[name] = self.__container.get(type_name)
        return resolved
