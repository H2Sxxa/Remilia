import json
import re
from functools import partialmethod
from types import ModuleType
from typing import (
    Callable,
    Dict,
    Generic,
    Optional,
    SupportsIndex,
    Type,
    Union,
    List,
)
from typing_extensions import Self
from inspect import signature

from .expression import ifElse, when
from .base.typings import NT, RT, T, VT


def hasInstance(cls: T) -> T:
    setattr(cls, "instance", cls())
    return cls


def toInstance(cls: Type[T]) -> T:
    return cls()


class InstanceMeta(type):
    def __new__(cls, *_) -> Self:
        setattr(cls, "instance", cls())
        return super.__new__(cls, *_)


def hasInstanceWithArgs(*args, **kwargs) -> T:
    def hasInstanceWrap(cls: Type[T]) -> T:
        setattr(cls, "instance", cls(*args, **kwargs))
        return cls

    return hasInstanceWrap


def toInstanceWithArgs(*args, **kwargs) -> T:
    def toInstanceWrap(cls: Type[T]) -> T:
        return cls(*args, **kwargs)

    return toInstanceWrap


def propertyOf(target: Callable, *args, **kwargs):
    def wrap(_) -> property:
        def argwarp(self):
            return target(self, *args, **kwargs)

        return property(argwarp)

    return wrap


def implBy(target, name: Optional[str] = None):
    def wrap(_: T) -> T:
        return lambda *args, **kwargs: getattr(
            target, _.__name__ if name is None else name
        )(*args, **kwargs)

    return wrap


def redirectTo(target: Callable):
    def wrap(_: T) -> T:
        return target

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
                try:
                    return float("0" + string)
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


class Option(Generic[T]):
    def __init__(self, val: T) -> None:
        super().__init__()
        self.__val = val

    def unwrap(self) -> T:
        return self.__val

    def is_empty(self) -> bool:
        return self.__val is None

    def unwrap_else(self, elseval: T) -> T:
        return elseval if self.is_empty() else self.__val


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

    def __call__(self, string: str) -> Self:
        return self.concat(string)


class MarkDownBuilder(StringBuilder):
    def title(self, level: int, text: str) -> Self:
        return self.concat("%s %s" % ("#" * level, text)).newline

    title1 = partialmethod(title, 1)
    title2 = partialmethod(title, 2)
    title3 = partialmethod(title, 3)
    title4 = partialmethod(title, 4)
    title5 = partialmethod(title, 5)
    title6 = partialmethod(title, 6)

    def warp(self, symbol: str, text: str) -> Self:
        return self.concat(f"{symbol}%s{symbol}" % text)

    bold = partialmethod(warp, "**")
    italic = partialmethod(warp, "*")
    deline = partialmethod(warp, "~~")

    def block(self, symbol: str, *texts: str) -> Self:
        return (
            self.newline.concat(symbol)
            .newline.concat("\n".join(texts))
            .newline.concat(symbol)
        )

    codeblock = partialmethod(block, "```")

    def hyperlink(self, text: str = "", uri: str = ""):
        return self.concat("[%s](%s)" % (text, uri))

    def image(self, text: str = "", imageuri: str = ""):
        return self.concat("!").hyperlink(text, imageuri)

    def startwith(self, symbol: str, text: str) -> Self:
        return self.concat("%s %s" % (symbol, text))

    quote = partialmethod(startwith, ">")
    unorderlist = partialmethod(startwith, "-")

    def orderlist(self, num: Union[str, int], text: str) -> Self:
        return self.startwith(num, text)

    @property
    def horizontal_rule(self):
        return self.newline2("---").newline2

    @property
    def newline2(self) -> Self:
        return self.newlinen(2)
