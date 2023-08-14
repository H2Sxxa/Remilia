import json
import re
from types import ModuleType
from typing import Callable, Dict, Generic, NoReturn, SupportsIndex, Type, Union, List
from typing_extensions import Self
from inspect import signature
from .base.typings import NT, T, VT


def hasInstance(cls: T) -> T:
    setattr(cls, "instance", cls())
    return cls


def toInstance(cls: T) -> T:
    return cls()


def hasInstanceWithArgs(*args, **kwargs) -> T:
    def hasInstanceWrap(cls: T) -> T:
        setattr(cls, "instance", cls(*args, **kwargs))
        return cls

    return hasInstanceWrap


def toInstanceWithArgs(*args, **kwargs) -> T:
    def toInstanceWrap(cls: T) -> T:
        return cls(*args, **kwargs)

    return toInstanceWrap


def propertyOf(target: Callable, *args, **kwargs):
    def wrap(_) -> property:
        def argwarp(self):
            return target(self, *args, **kwargs)

        return property(argwarp)

    return wrap


def typedet(string: str, strict=True) -> any:
    if (
        not re.match(r"[\u4E00-\u9FA5A-Za-z]", string)
        and re.match(r"[0-9]", string)
        and not re.match(
            r"[`~!@#$%^&*()_\-+=<>?:\"{}|,\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]",
            string,
        )
    ):
        if "." in string:
            try:
                return float(string)
            except:
                pass
        else:
            return int(string)
    try:
        res = json.loads(string, strict=strict)
        return res
    except:
        pass
    return string


class NameSpace(dict):
    def updateModules(self, *modules: ModuleType) -> Self:
        for module in modules:
            self.update(module.__dict__)
        return self

    def updateElements(self, *elements: Type) -> Self:
        self.updateModule([element.__module__.__dict__ for element in elements])
        return self

    def updateVal(self, obj: Union[Type, ModuleType]) -> Self:
        try:
            self.updateElements(obj)
        except:
            self.updateModules(obj)
        return self

    def updateNV(self, name: NT, value: VT) -> Self:
        self.update({name: value})
        return self

    def updateDict(self, *dicts: Dict[str, Type]) -> Self:
        for kv in dicts:
            self.update(kv)
        return self

    def to_dict(self) -> Dict[str, Type]:
        return dict(self)

    @propertyOf(to_dict)
    def prop_dict(self) -> Dict[str, Type]:
        ...

    @staticmethod
    def fromModules(*module: ModuleType) -> Self:
        return NameSpace().updateModule(*module)

    @staticmethod
    def fromElements(*elements: Type) -> Self:
        return NameSpace().updateElements(*elements)


class LinkTun(Generic[T]):
    __back: T

    def setBack(self, back: T) -> Self:
        self.__back = back
        return self

    def backto(self) -> T:
        return self.__back


class Signs:
    @staticmethod
    def getParasAsType(call: Callable):
        return [signarg.annotation for _, signarg in signature(call).parameters.items()]

    @staticmethod
    def check_eq(paraa: List[Type], parab: List[Type]) -> bool:
        if len(paraa) != len(parab):
            return False
        else:
            for a, b in zip(paraa, parab):
                if a != b:
                    return False
            return True


class StringBuilder:
    def __init__(self, __string: str = str()) -> None:
        self.__string = __string

    def replace(self, __old: str, __new: str, __count: SupportsIndex = -1) -> Self:
        self.__string = self.__string.replace(__old, __new, __count)
        return self

    @property
    def newline(self) -> Self:
        self.__string += "\n"
        return self

    def newlinen(self, __n: int) -> Self:
        self.__string += "\n" * __n
        return self

    @property
    def space(self) -> Self:
        self.__string += " "
        return self

    def spacen(self, __n: int) -> Self:
        self.__string += " " * __n
        return self

    @property
    def space4(self) -> Self:
        self.__string += " " * 4
        return self

    def concat(self, __string: str):
        self.__string += __string
        return self

    def ifElse(
        self,
        condition: Callable[[], bool] = lambda: True,
        ifdo: str = "",
        elsedo: str = "",
    ) -> Self:
        ifElse(
            condition,
            ifdo=lambda: self.concat(ifdo),
            elsedo=lambda: self.concat(elsedo),
        )
        return self

    def when(
        self,
        condition: Callable[[], bool] = lambda: True,
        ifdo: str = "",
    ) -> Self:
        when(
            condition,
            ifdo=lambda: self.concat(ifdo),
        )
        return self

    def clear(self) -> Self:
        self.__string = str()
        return self

    def get(self) -> str:
        return self.__string

    def __str__(self) -> str:
        return self.__string


def ifElse(
    condition: Union[Callable[[], bool], bool] = lambda: True,
    ifdo: Callable[[], NT] = lambda: None,
    elsedo: Callable[[], VT] = lambda: None,
) -> Union[NT, VT]:
    if isinstance(condition, Callable):
        condition = condition()
    return ifdo() if condition else elsedo()


def when(
    condition: Union[Callable[[], bool], bool] = lambda: True,
    whendo: Callable[[], T] = lambda: None,
) -> T:
    if isinstance(condition, Callable):
        condition = condition()
    return whendo() if condition else None


def exception(exc: Exception = Exception()) -> NoReturn:
    raise exc
