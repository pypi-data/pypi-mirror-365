# Внедрение зависимостей

Для управления зависимостями внутри приложения используется контейнер pysr-container

- Cовместим с [pysr-abc-container](https://qbrick-framework.ru/python/standard/pysr-abc-container).
- Обнаруживает циклические ссылки.
- Принимает определения в виде словаря.


## Типы определений

Контейнер в версии 0.1.0 поддерживает следующие типы определений:

### Значение

Определение типа `Value` вернет установленное значение как есть. В данном случае значение переменной obj - тип SomeClass:

```python
from pysr_container import Container
from pysr_container.definitions import Value

class SomeClass: ...

container = Container({
	SomeClass: Value(SomeClass)
})

obj = container.get(SomeClass)
```

### Ссылка

Один ключ контейнера может предоставлять значение, сохраненной в контейнер по другому ключу. Для этого используется определение `Reference`. В данном случае значение переменной obj - тип SomeClass:

```python
from pysr_container import Container
from pysr_container.definitions import Value, Reference

class SomeClass: ...

container = Container({
	SomeClass: Value(SomeClass),
    'ref': Reference(SomeClass)
})

obj = container.get('ref')
```

### Объект

Определение типа `Object` при получении из контейнера предпримет попытку создать объект заданного класса с заданными параметрами. Если конструктор получаемого класса содержит параметры, для которых определен тип и которые не переданы в явном виде, будет предпринята попытка получить объекты этих типов из контейнера:

```python
from pysr_container import Container
from pysr_container.definitions import Object

class Foo:
    @property
    def name(self):
        return 'Foo'

class Bar:
    def __init__(self, name, foo: Foo):
        self.__foo = foo
        self.__name = name
    @property
    def name(self):
        return self.__foo.name + self.__name

container = Container({
    Foo: Object(Foo),
    Bar: Object(Bar, {'name': 'Bar'})
})

obj = container.get(Bar)

print(obj.name)  # выведет FooBar
```


