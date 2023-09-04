from abc import abstractmethod
from inspect import signature
from typing import Callable, Dict, List, Type
from typing_extensions import Self
from Remilia.base.typings import RT, T, Empty
from .base.models import SingleArg


class Signs:
    @staticmethod
    def getParasAsType(func: Callable):
        return [signarg.annotation for _, signarg in signature(func).parameters.items()]

    @staticmethod
    def getParas(func: Callable):
        return [
            SingleArg(
                arg_name=name,
                arg_type=signarg.annotation,
                arg_default=signarg.default,
                arg_index=index,
            )
            for index, (name, signarg) in enumerate(signature(func).parameters.items())
        ]

    @staticmethod
    def check_eq(paraa: List[Type], parab: List[Type]) -> bool:
        if len(paraa) != len(parab):
            return False
        else:
            for a, b in zip(paraa, parab):
                if a != b:
                    return False
            return True


class DependObs:
    __f: Callable[..., RT]
    __i: Dict[str, T]

    def __init__(self, func: Callable[..., RT]) -> None:
        self.__f = func
        self.__i = {}
        for sa in Signs.getParas(self.__f):
            if issubclass(sa.arg_type, BeDepend) and sa.arg_default == Empty:
                self.__i.update({sa.arg_name: sa.arg_type.get_dependence()})

    def __call__(self, *args, **kwargs) -> RT:
        return self.__f(*args, **{**kwargs, **self.__i})


def Depend(func: T) -> T:
    return DependObs(func)


class _BeDependInstance(type):
    def __new__(cls, name, bases, attr) -> Self:
        attr["get_dependence"] = lambda *_: cls.__new__(cls, name, bases, attr)()
        return super().__new__(cls, name, bases, attr)


class BeDepend:
    @staticmethod
    @abstractmethod
    def get_dependence() -> Self:
        raise TypeError(
            "unimplement abstract method `get_dependence`, consider extend `BeDepend` or try extend `BeDependInstance`"
        )


class BeDependInstance(BeDepend, metaclass=_BeDependInstance):
    def get_dependence() -> Self:
        ...
