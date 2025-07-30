class Function:

    def __init__(self, function, arguments: dict = None):
        self.__function = function
        self.__arguments = arguments

    def __call__(self):
        return self.__function(**self.__arguments)

    def has_arguments(self) -> bool:
        return len(self.__arguments) > 0

    @property
    def arguments(self) -> dict:
        return self.__arguments or {}
