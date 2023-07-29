from gc import get_referents
from abc import abstractmethod
from enum import Enum
from types import MethodType
from typing import Any, Dict, List, Type, Union, Callable
from inspect import getsourcelines
from typing_extensions import Self
from pydantic import BaseModel


from .base.exceptions import MixinError


class At(Enum):
    INVOKE = "mixin_invoke"
    HEAD = "mixin_head"
    RETURN = "mixin_return"
    AFTER_RETURN = "mixin_after_return"

    INJECT_BEFORE = "mixin_inject_after"
    INJECT_OVERWRITE = "mixin_inject_overwrite"
    INJECT_AFTER = "mixin_inject_after"

    DEFAULT = "mixin"


MIXIN_CONFIGS = "__mixin_configs__"

_freeze_action: List[Dict[str, object]] = []


def mixin_getattr(__o: object, __name: str, __gc=False) -> Any:
    if __gc:
        return get_referents(__o.__dict__)[0][__name]
    else:
        return getattr(__o, __name)


def mixin_delattr(__o: object, __name: str, __gc=False) -> None:
    if __gc:
        get_referents(__o.__dict__)[0].pop(__name)
    else:
        delattr(__o, __name)


def mixin_setattr(__o: object, __name: str, __value: Any, __gc=False) -> None:
    if __gc:
        get_referents(__o.__dict__)[0][__name] = __value
    else:
        setattr(__o, __name, __value)


def mixin_hasattr(__o: object, __name: str, __gc=False) -> None:
    if __gc:
        return get_referents(__o.__dict__)[0].__contains__(__name)
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
        _freeze_action.clear()
        return mixincls


class MixinConfigs(BaseModel):
    target: list = []
    mixincls: object = object()
    mixin: object = Mixin(None)
    gc: bool = None


class MixinTools(BaseModel):
    getattr: Callable = mixin_getattr
    setattr: Callable = mixin_setattr
    hasattr: Callable = mixin_hasattr
    delattr: Callable = mixin_delattr


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
        return self.mixintools.getattr(__o, __name, self.gc)

    def mixin_setattr(self, __o: object, __name: str, __value: Any) -> None:
        return self.mixintools.setattr(__o, __name, __value, self.gc)

    def mixin_delattr(self, __o: object, __name: str, __value: Any) -> None:
        return self.mixintools.delattr(__o, __name, __value, self.gc)

    def mixin_hasattr(self, __o: object, __name: str) -> bool:
        return self.mixintools.hasattr(__o, __name, self.gc)

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
            _freeze_action.append({"init": self.init, "arg": (mixinmethod,)})
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

    def addkwargs(self, **kwargs):
        [setattr(self, n, v) for n, v in kwargs]
        return self

    def cast(
        subself,
        at: At,
        method: Union[str, MethodType, None] = None,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ) -> Self:
        return subself().new(at, method, gc, mixintools)

    def new(
        self,
        at: At,
        method: Union[str, MethodType, None] = None,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ) -> Self:
        self.at = at
        self.method = method
        self.gc = gc
        self.mixintools = mixintools
        return self


class MethodGlue:
    pass


class CodeOperator:
    def __init__(self, method: Callable, completion: bool = True) -> None:
        self.codes = list(getsourcelines(method)[0])
        self.name = method.__name__
        self.base_indent = self.get_indent(self.codes[0]) * " "
        self.extra_indent = self.get_indent(self.codes[1]) * " "
        self.completion = completion

    def completion_code(self, code: str) -> str:
        if self.completion:
            return "%s%s\n" % (self.extra_indent, code)
        else:
            return code

    def insert(self, line: int, code: str) -> Self:
        self.codes.insert(line, self.completion_code(code))
        return self

    def insertlines(self, line: int, codes: List[str]) -> Self:
        for code in codes:
            self.codes.insert(line, self.completion_code(code))
            line += 1
        return self

    def insert_head(self, code: str) -> Self:
        self.codes.insert(1, self.completion_code(code))
        return self

    def insertlines_head(self, codes: List[str]) -> Self:
        self.insertlines(1, codes)
        return self

    def insert_end(self, code: str) -> Self:
        self.codes.insert(-1, self.completion_code(code))
        return self

    def insertlines_end(self, codes: List[str]) -> Self:
        self.extend([self.completion_code(code) for code in codes])
        return self

    def replace(self, line: int, code: str) -> Self:
        self.codes[line] = self.completion_code(code)
        return self

    def append(self, code: str) -> Self:
        self.codes.append(self.completion_code(code))
        return self

    @staticmethod
    def get_indent(string: str) -> int:
        num = 0
        for char in string:
            if char == " ":
                num += 1
            else:
                return num
        return num

    @staticmethod
    def codesformat(codes: List[str]) -> List[str]:
        extra_indent = CodeOperator.get_indent(codes[1]) * " "
        codes.pop(0)
        return [code.replace(extra_indent, "", 1) for code in codes]

    @staticmethod
    def getCodelinesFromCallable(method: Callable) -> List[str]:
        return CodeOperator.codesformat(list(getsourcelines(method)[0]))

    @staticmethod
    def getCodeFromCallable(method: Callable) -> str:
        return "".join(CodeOperator.getCodelinesFromCallable(method))

    def export(self, namespace: dict = {}) -> Callable:
        exec(
            "".join([code.replace(self.base_indent, "", 1) for code in self.codes]),
            namespace,
        )
        return namespace[self.name]


class Accessor(MixinBase):
    def mixin(self) -> None:
        property_name = "_%s%s" % (self.configs.mixincls.__name__, self.method)
        pre = [
            self.mixin_setattr(
                t,
                property_name,
                lambda _: mixin_getattr(
                    _, "_%s%s" % (_.__class__.__name__, self.method)
                ),
            )
            for t in self.configs.target
        ]
        warp = [
            self.mixin_setattr(
                t, property_name, property(self.mixin_getattr(t, property_name))
            )
            for t in self.configs.target
        ]
        return [pre, warp]

    @staticmethod
    def withValue(
        method: Union[str, MethodType, None] = None,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ):
        return Accessor.cast(Accessor, None, method, gc, mixintools).init


class Inject(MixinBase):
    @staticmethod
    def withValue(
        at: At,
        method: Union[str, MethodType, None] = None,
        line: Union[None, int] = None,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ):
        """
        use line when at -> INJECT_ ...

        """
        return Inject.cast(Inject, at, method, gc, mixintools).addkwargs(line=line).init


class OverWrite(MixinBase):
    def mixin(self) -> None:
        return [
            self.mixin_setattr(t, self.method, self.mixinmethod)
            for t in self.configs.target
        ]

    @staticmethod
    def withValue(
        method: Union[str, MethodType, None] = None,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ):
        return OverWrite.cast(OverWrite, None, method, gc, mixintools).init
