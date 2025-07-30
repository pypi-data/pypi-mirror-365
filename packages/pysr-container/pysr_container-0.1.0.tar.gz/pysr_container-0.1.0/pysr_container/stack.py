from .exceptions import CircularDependencyError


class Stack:
    def __init__(self):
        self.__stack = {}

    def push(self, item):
        if item in self.__stack:
            if not self.__stack[item]:
                raise CircularDependencyError(f'Unable to resolve "{item}", circular dependency detected')
        else:
            self.__stack[item] = False

    def mark_as_resolved(self, item):
        self.__stack[item] = True
