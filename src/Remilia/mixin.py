from gc import get_referents
from abc import abstractmethod
from enum import Enum
from types import MethodType
from typing import Any, Dict, List, Type, Union, Callable
from typing_extensions import Self
from pydantic import BaseModel


from .base.exceptions import MixinError


class At(Enum):
    BEFORE_INVOKE = "mixin_before_invoke"
    INVOKE = "mixin_invoke"
    HEAD = "mixin_head"
    RETURN = "mixin_return"
    AFTER_RETURN = "mixin_after_return"
    DEFAULT = "mixin"


MIXIN_CONFIGS = "__mixin_configs__"

_freeze_action:List[Dict[str,object]]=[]

def mixin_getattr(__o: object, __name: str, __gc=False) -> Any:
    if __gc:
        return get_referents(__o.__dict__)[__name]
    else:
        return getattr(__o, __name)


def mixin_setattr(__o: object, __name: str, __value: Any, __gc=False) -> None:
    if __gc:
        get_referents(__o.__dict__)[__name] = __value
    else:
        setattr(__o, __name, __value)


def mixin_hasattr(__o: object, __name: str, __gc=False) -> None:
    if __gc:
        return get_referents(__o.__dict__).__contains__(__name)
    else:
        return hasattr(__o, __name)


class Mixin:
    target: List[Type]
    debuginfo: List[Exception]
    gc: bool

    def __init__(self, target: Union[List[Type], Type], gc: bool = False) -> None:
        if not isinstance(target, list):
            self.target = [target]
        else:
            self.target = target
        self.debuginfo = []
        self.gc = gc

    def __call__(self, mixincls: Type) -> Type:
        self.configs = MixinConfigs(
            target=self.target, mixincls=mixincls, mixin=self, gc=self.gc
        )
        for mname in dir(mixincls):
            try:
                obj = getattr(mixincls, mname)
                if isinstance(obj, Callable):
                    setattr(obj, MIXIN_CONFIGS, self.configs)
            except Exception as e:
                self.debuginfo.append(e)
        for fa in _freeze_action:
            fa["init"](*fa["arg"])
        return mixincls


class MixinConfigs(BaseModel):
    target: list = []
    mixincls: object = object()
    mixin: object = Mixin(None)
    gc: bool = None


class MixinCallable(Callable):
    @property
    def __mixin_configs__(self) -> List[Type]:
        return [...]


def getConfigs(mcallable: MixinCallable) -> MixinConfigs:
    return mcallable.__mixin_configs__


class MixinBase:
    at: At
    gc: bool
    method: str
    mixinmethod: MethodType
    configs: MixinConfigs
    
    @abstractmethod
    def mixin(self) -> None:
        ...

    @abstractmethod
    def mixin_before_invoke(self) -> None:
        ...

    @abstractmethod
    def mixin_invoke(self) -> None:
        ...

    @abstractmethod
    def mixin_head(self) -> None:
        ...

    @abstractmethod
    def mixin_return(self) -> None:
        ...

    @abstractmethod
    def mixin_after_return(self) -> None:
        ...

    def mixin_getattr(self, __o: object, __name: str) -> Any:
        return mixin_getattr(__o, __name, self.gc)

    def mixin_setattr(self, __o: object, __name: str, __value: Any) -> None:
        return mixin_setattr(__o, __name, __value, self.gc)

    def mixin_hasattr(self, __o: object, __name: str) -> bool:
        return mixin_hasattr(__o, __name, self.gc)

    def match_at(self) -> None:
        if self.at == None:
            return self.mixin()
        if not hasattr(self, self.at):
            raise MixinError("%s not support %s" % (self, self.at))
        else:
            atmixin: MethodType = getattr(self, self.at)
            if getattr(atmixin, "__isabstractmethod__") == True:
                raise MixinError("%s not support %s" % (self, self.at))
            atmixin()

    def init(self, mixinmethod: MethodType):
        try:
            self.configs = getConfigs(mixinmethod)
        except:
            _freeze_action.append({"init":self.init,"arg":(mixinmethod,)})
            return mixinmethod
        self.mixinmethod = mixinmethod
        if self.method == None:
            self.method = mixinmethod.__name__
        elif isinstance(self.method, str):
            pass
        else:
            self.method = self.method.__name__
        if self.gc == None:
            self.gc = self.configs.gc
        self.match_at()
        return mixinmethod

    def cast(
        subself, at: At, method: Union[str, MethodType, None] = None, gc: bool = None
    ) -> Callable[[MethodType], MethodType]:
        return subself().new(at, method, gc).init

    def new(
        self, at: At, method: Union[str, MethodType, None] = None, gc: bool = None
    ) -> Self:
        self.at = at
        self.method = method
        self.gc = gc
        return self


class Inject(MixinBase):
    @staticmethod
    def withValue(at: At, method: Union[str, MethodType, None] = None, gc: bool = None):
        return Inject.cast(Inject, at, method, gc)


class Redirect(MixinBase):
    @staticmethod
    def withValue(at: At, method: Union[str, MethodType, None] = None, gc: bool = None):
        return Redirect.cast(Redirect, at, method, gc)


class OverWrite(MixinBase):
    def mixin(self) -> None:
        return [
            self.mixin_setattr(t, self.method, self.mixinmethod)
            for t in self.configs.target
        ]

    @staticmethod
    def withValue(method: Union[str, MethodType, None] = None, gc: bool = None):
        return OverWrite.cast(OverWrite, None, method, gc)
