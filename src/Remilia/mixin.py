from gc import get_referents
from abc import abstractmethod
from enum import Enum
from types import MethodType
from typing import Any, Dict, List, Tuple, Type, Union, Callable
from inspect import getsourcelines
from typing_extensions import Self
from pydantic import BaseModel

from .base.exceptions import MixinError


class At(Enum):
    # Inject stuff
    HEAD = "mixin_head"
    INSERT = "mixin_insert"
    # Glue
    INVOKE = "mixin_invoke"
    RETURN = "mixin_return"
    # Generic
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


class CallableArgs:
    args: Tuple[Any] = ()
    kwargs: Dict[str, Any] = {}

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs.update(kwargs)


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
    def mixin_head(self) -> None:
        ...

    @abstractmethod
    def mixin_insert(self) -> None:
        ...

    @abstractmethod
    def mixin_invoke(self) -> None:
        ...

    @abstractmethod
    def mixin_return(self) -> None:
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
        if not hasattr(self, self.at.value):
            raise MixinError("%s not support %s" % (self, self.at.name))
        else:
            atmixin: MethodType = getattr(self, self.at.value)
            if hasattr(atmixin, "__isabstractmethod__"):
                if getattr(atmixin, "__isabstractmethod__") == True:
                    raise MixinError("%s not support %s" % (self, self.at.name))
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
        for n, v in kwargs.items():
            setattr(self, n, v)
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


class CodeOperator:
    def __init__(self, method: Callable, completion: bool = True) -> None:
        self.codes = list(getsourcelines(method)[0])
        self.name = method.__name__
        self.base_indent = self.get_indent(self.codes[0]) * " "
        self.codes = self.commonformat(self.codes, self.base_indent)
        self.extra_indent = self.get_indent(self.codes[1]) * " "
        self.completion = completion

    def poplines(self, *lines) -> Self:
        add = 0
        for line in lines:
            self.codes.pop(line - add)
            add += 1
        return self

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
    def commonformat(codes: List[str], base_indent: str):
        return [
            code
            for code in [code.replace(base_indent, "", 1) for code in codes]
            if code[0] != "@"
        ]

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
        base_indent = CodeOperator.get_indent(codes[0]) * " "
        codes = CodeOperator.commonformat(codes, base_indent)
        extra_indent = CodeOperator.get_indent(codes[1]) * " "
        codes.pop(0)
        return [code.replace(extra_indent, "", 1) for code in codes]

    @staticmethod
    def remove_unexpectlines(codes: List[str]):
        return [code[:-1] if code[-2::] else code for code in codes]

    @staticmethod
    def getCodelinesFromCallable(method: Callable) -> List[str]:
        return CodeOperator.remove_unexpectlines(
            CodeOperator.codesformat(list(getsourcelines(method)[0]))
        )

    @staticmethod
    def getCodeFromCallable(method: Callable) -> str:
        return "".join(CodeOperator.getCodelinesFromCallable(method))

    def export(self, namespace: dict = {}) -> Callable:
        exec(
            "".join(self.codes),
            namespace,
        )
        return namespace[self.name]


class Glue(MixinBase):
    def mixin_invoke(self) -> None:
        for t in self.configs.target:
            self.rawmethod: MethodType = self.mixin_getattr(t, self.method)

            def glue_invoke(*args, **kwargs):
                cargs: CallableArgs
                cargs = self.mixinmethod(*args, **kwargs)
                return self.rawmethod(*cargs.args, **cargs.kwargs)

            self.mixin_setattr(t, self.method, glue_invoke)

    def mixin_return(self) -> None:
        for t in self.configs.target:
            self.rawmethod: MethodType = self.mixin_getattr(t, self.method)

            def glue_invoke(*args, **kwargs):
                result=self.rawmethod(*args, **kwargs)
                return self.mixinmethod(args[0],result)

            self.mixin_setattr(t, self.method, glue_invoke)

    def mixin(self) -> None:
        self.mixin_return()

    @staticmethod
    def withValue(
        method: Union[str, MethodType, None] = None,
        gc: bool = None,
        at: At = None,
        mixintools: MixinTools = MixinTools(),
    ):
        return Glue.cast(Glue, at, method, gc, mixintools).init


class Accessor(MixinBase):
    def mixin(self) -> None:
        property_name = "_%s%s" % (self.configs.mixincls.__name__, self.method)
        for t in self.configs.target:
            self.mixin_setattr(
                t,
                property_name,
                lambda _: mixin_getattr(
                    _, "_%s%s" % (_.__class__.__name__, self.method)
                ),
            )
            self.mixin_setattr(
                t,
                self.method,
                lambda _: mixin_getattr(
                    _, "_%s%s" % (_.__class__.__name__, self.method)
                ),
            )
            self.mixin_setattr(
                t, property_name, property(self.mixin_getattr(t, property_name))
            )
            self.mixin_setattr(
                t, self.method, property(self.mixin_getattr(t, self.method))
            )

    @staticmethod
    def withValue(
        method: Union[str, MethodType, None] = None,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ):
        return Accessor.cast(Accessor, None, method, gc, mixintools).init


class Inject(MixinBase):
    insertline: int
    poplines: List[int]
    namespace: Dict[str, object]

    def mixin(self) -> None:
        self.mixin_head()

    def mixin_head(self) -> None:
        codes = CodeOperator.getCodelinesFromCallable(self.mixinmethod)
        for target in self.configs.target:
            method = (
                CodeOperator(getattr(target, self.method))
                .insertlines_head(codes)
                .export(self.namespace)
            )
            self.mixin_setattr(target, self.method, method)

    def mixin_insert(self) -> None:
        codes = CodeOperator.getCodelinesFromCallable(self.mixinmethod)
        # numcodes = len(codes)
        if self.insertline == None:
            self.mixin_head()
        if isinstance(self.poplines, int):
            self.poplines = [self.poplines]
        for target in self.configs.target:
            method = (
                CodeOperator(getattr(target, self.method))
                .insertlines(self.insertline, codes)
                .poplines(*[line for line in self.poplines])
                .export(self.namespace)
            )
            self.mixin_setattr(target, self.method, method)

    @staticmethod
    def withValue(
        at: At,
        method: Union[str, MethodType, None] = None,
        insertline: Union[None, int] = None,
        poplines: Union[int, List[int]] = [],
        namespace: Dict[str, object] = {},
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ):
        return (
            Inject.cast(Inject, at, method, gc, mixintools)
            .addkwargs(
                insertline=insertline,
                poplines=poplines,
                namespace=namespace,
            )
            .init
        )


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
