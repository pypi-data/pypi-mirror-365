from typing import Union, final
from pysr_abc_container import ContainerInterface
from ..contract import DefinitionInterface


@final
class Reference(DefinitionInterface):
    """
    Определение - ссылка.
    При разрешении возвращает запись контейнера, на которую ссылается по идентификатору.
    """

    def __init__(self, to: Union[str, type]):
        self.__to = to

    def resolve(self, container: ContainerInterface):
        return container.get(self.__to)
