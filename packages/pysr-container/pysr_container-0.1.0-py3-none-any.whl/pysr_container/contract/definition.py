from abc import ABC, abstractmethod
from pysr_abc_container import ContainerInterface


class DefinitionInterface(ABC):
    """
    Интерфейс определения.
    """
    @abstractmethod
    def resolve(self, container: ContainerInterface):
        raise NotImplementedError
