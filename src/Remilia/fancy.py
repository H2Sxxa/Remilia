import json
import re
from types import ModuleType
from typing import Callable, Dict, Type
from typing_extensions import Self

from .base.typings import T


def hasInstance(cls: T) -> T:
    setattr(cls, "instance", cls())
    return cls


def hasInstanceWithArgs(*args, **kwargs) -> T:
    def hasInstanceWrap(cls: T) -> T:
        setattr(cls, "instance", cls(*args, **kwargs))
        return cls

    return hasInstanceWrap


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
    def updateModule(self, *modules: ModuleType) -> Self:
        for module in modules:
            self.update(module.__dict__)
        return self

    def updateElements(self, *elements: Type) -> Self:
        self.updateModule([element.__module__.__dict__ for element in elements])
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
