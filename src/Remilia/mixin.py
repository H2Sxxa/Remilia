from gc import get_referents
from abc import abstractmethod
from enum import Enum
from types import MethodType
from typing import Any, Dict, Iterable, List, Tuple, Type, Union, Callable
from inspect import getsourcelines
from typing_extensions import Self
from pydantic import BaseModel

from .log import get_logger
from .fancy import NameSpace, hasInstance
from .base.exceptions import CodeOperatorError, MixinError
from .base.models import Args

class At(Enum):
    # Inject stuff
    HEAD = "mixin_head"
    INSERT = "mixin_insert"
    END = "mixin_end"
    # Glue
    INVOKE = "mixin_invoke"
    RETURN = "mixin_return"
    # Generic
    DEFAULT = "mixin"


MIXIN_CONFIGS = "__mixin_configs__"

_freeze_action: List[Dict[str, object]] = []
_freeze_corobject: Dict[str, object] = {}


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


class Ancestor:
    target: List[Type]
    at: At
    ancestor_namespace: Dict[str, object]
    ancestor_exclude: List[Type]

    def __init__(
        self,
        target: Union[List[Type], Type],
        ancestor_namespace: Union[List[Dict[str, Type]], Dict[str, Type]] = {},
        ancestor_exclude: Union[List[Type], Type] = [],
        at: At = At.END,
        ancestor_hook: Callable[[List[Type]], Iterable] = lambda _: _,
    ) -> None:
        if not isinstance(target, Iterable):
            self.target = [target]
        else:
            self.target = target
        if not isinstance(ancestor_exclude, Iterable):
            self.ancestor_exclude = [ancestor_exclude]
        else:
            self.ancestor_exclude = ancestor_exclude

        if not isinstance(ancestor_namespace, Iterable) or isinstance(
            ancestor_namespace, Dict
        ):
            self.ancestor_namespace = [ancestor_namespace]
        else:
            self.ancestor_namespace = ancestor_namespace

        self.at = at
        self.ancestor_hook = ancestor_hook

    def __call__(self, mixincls) -> Type:
        for t in self.target:
            t: object
            if t.__bases__ == (object,):
                t = type(t.__name__, (mixincls,), dict(t.__dict__))
            else:
                rebuild_bases = tuple(
                    self.ancestor_hook(
                        [cls for cls in t.__bases__ if cls not in self.ancestor_exclude]
                    )
                )

                if self.at == At.HEAD:
                    t.__bases__ = (
                        mixincls,
                        *rebuild_bases,
                    )
                else:
                    t.__bases__ = (*rebuild_bases, mixincls)
            for ans in self.ancestor_namespace:
                ans.update({t.__name__: t})
        return mixincls


class Mixin:
    target: List[Type]
    debuginfo: List[Exception]
    gc: bool

    def __init__(
        self,
        target: Union[List[Type], Type],
        gc: bool = False,
    ) -> None:
        if not isinstance(target, Iterable):
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
    def mixin_head(self) -> None:
        ...

    @abstractmethod
    def mixin_end(self) -> None:
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


class EnumCOChar(Enum):
    EMPTY = ""
    DELETELINE = "$DELETELINE"
    SPACE = " "
    SPACE4 = "    "
    SPACE8 = "        "


_COCS: Dict[str, EnumCOChar] = {}
for cocn in dir(EnumCOChar):
    coc = getattr(EnumCOChar, cocn)
    if isinstance(coc, EnumCOChar):
        _COCS.update({str(coc): coc})


class CodeOperator:
    def __init__(
        self, method: MethodType, completion: bool = True, debugmode: bool = False
    ) -> None:
        self.fullname = "%s.%s" % (method.__module__, method.__qualname__)
        self.codes = list(CodeOperator.getsourcelines(method)[0])
        self.name = method.__name__
        self.base_indent = self.get_indent(self.codes[0]) * " "
        self.codes = self.commonformat(self.codes, self.base_indent)
        self.extra_indent = self.get_indent(self.codes[1]) * " "
        self.completion = completion
        self.debugmode = debugmode

    @staticmethod
    def getsourcelines(__obj: object) -> List[str]:
        fullname = "%s.%s" % (__obj.__module__, __obj.__qualname__)
        if _freeze_corobject.__contains__(fullname):
            return [_freeze_corobject[fullname], len(_freeze_corobject[fullname])]
        return getsourcelines(__obj)

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
            if line >= 0:
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
        self.codes.extend([self.completion_code(code) for code in codes])
        return self

    def replace(self, line: int, code: str) -> Self:
        self.codes[line] = self.completion_code(code)
        return self

    def append(self, code: str) -> Self:
        self.codes.append(self.completion_code(code))
        return self

    @staticmethod
    def commonformat(codes: List[str], base_indent: str):
        exclude_codes = []
        for code in codes:
            if "def " not in code:
                exclude_codes.append(code)
            else:
                break

        codes = [code for code in codes if code not in exclude_codes]

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
            CodeOperator.codesformat(list(CodeOperator.getsourcelines(method)[0]))
        )

    @staticmethod
    def getCodeFromCallable(method: Callable) -> str:
        return "".join(CodeOperator.getCodelinesFromCallable(method))

    def coc_translate(self, code: str):
        code = code.replace("#!", "")
        for name, coc in _COCS.items():
            symbol = "%s;" % name
            if coc == EnumCOChar.DELETELINE:
                code = "\n".join(
                    [fcode for fcode in code.split("\n") if symbol not in fcode]
                )
            else:
                code = code.replace(symbol, coc.value)
        return code

    def export(self, namespace: dict = {}) -> Callable:
        bake_codes = [self.coc_translate(code) for code in self.codes]
        code = "".join(bake_codes)
        if self.debugmode:
            logger = get_logger()
            logger_level = logger.vlevel
            logger.set_vlevel(10)
            logger.warn(
                "CodeOperator under debugmode , remove the 'debugmode = True' to close"
            )
            logger.info(bake_codes)

            logger.info("\nexec code: \n %s" % (code))
            logger.set_vlevel(logger_level)
        try:
            exec(
                code,
                namespace,
            )
            method = namespace[self.name]
            _freeze_corobject.update({self.fullname: bake_codes})
            return method
        except Exception as e:
            raise CodeOperatorError(e)


class Glue(MixinBase):
    def mixin_invoke(self) -> None:
        for t in self.configs.target:
            self.rawmethod: MethodType = self.mixin_getattr(t, self.method)

            def glue_invoke(*args, **kwargs):
                cargs: Args
                cargs = self.mixinmethod(*args, **kwargs)
                return self.rawmethod(*cargs.args, **cargs.kwargs)

            self.mixin_setattr(t, self.method, glue_invoke)

    def mixin_return(self) -> None:
        for t in self.configs.target:
            self.rawmethod: MethodType = self.mixin_getattr(t, self.method)

            def glue_invoke(*args, **kwargs):
                result = self.rawmethod(*args, **kwargs)
                return self.mixinmethod(args[0], result)

            self.mixin_setattr(t, self.method, glue_invoke)

    def mixin(self) -> None:
        self.mixin_return()

    def func_init(self, mixinmethod: Callable) -> Callable:
        self.mixinmethod = mixinmethod
        if self.at == At.INVOKE:
            for cab in self.method:
                self.rawmethod = cab

                def glue_invoke(*args, **kwargs):
                    cargs: Args
                    cargs = self.mixinmethod(*args, **kwargs)
                    return self.rawmethod(*cargs.args, **cargs.kwargs)

                glue_invoke.__name__ = cab.__name__
                self.namespace.update({cab.__name__: glue_invoke})
        if self.at == At.RETURN:
            for cab in self.method:
                self.rawmethod = cab

                def glue_invoke(*args, **kwargs):
                    result = self.rawmethod(*args, **kwargs)
                    return self.mixinmethod(result)

                glue_invoke.__name__ = cab.__name__
                self.namespace.update({cab.__name__: glue_invoke})
        return mixinmethod

    @staticmethod
    def withFunc(
        func: Union[Callable, List[Callable]],
        namespace: NameSpace = NameSpace(),
        gc: bool = None,
        at: At = None,
        mixintools: MixinTools = MixinTools(),
    ):
        if not isinstance(func, Iterable):
            func = [func]
        return (
            Glue.cast(Glue, at, func, gc, mixintools)
            .addkwargs(namespace=namespace)
            .func_init
        )

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
    insertfirst: bool
    namespace: NameSpace
    debugmode: bool

    def mixin(self) -> None:
        self.mixin_head()

    def getNameSpace(self, target: Any):
        self.namespace = NameSpace(self.namespace)
        try:
            return self.namespace.updateElements(target)
        except:
            try:
                return self.namespace.updateModules(target)
            except:
                return self.namespace

    def doinsert(
        self,
        cor: CodeOperator,
        insertuse: MethodType,
        *insert_args,
        **insert_kwargs,
    ) -> CodeOperator:
        if self.insertfirst:
            cor = insertuse(
                *insert_args,
                **insert_kwargs,
            )
            cor.poplines(*[line for line in self.poplines])
        else:
            cor.poplines(*[line for line in self.poplines])
            cor = insertuse(
                *insert_args,
                **insert_kwargs,
            )
        return cor

    def rename_method(self, method: Callable, tomethod: Callable):
        method.__qualname__ = tomethod.__qualname__
        method.__module__ = tomethod.__module__
        return method

    def mixin_head(self) -> None:
        codes = CodeOperator.getCodelinesFromCallable(self.mixinmethod)
        for target in self.configs.target:
            self.namespace = self.getNameSpace(target)
            cor = CodeOperator(
                self.mixin_getattr(target, self.method), debugmode=self.debugmode
            )
            self.mixin_setattr(
                target,
                self.method,
                self.rename_method(
                    self.doinsert(cor, cor.insertlines_head, codes).export(
                        self.namespace
                    ),
                    self.mixin_getattr(target, self.method),
                ),
            )

    def mixin_end(self) -> None:
        codes = CodeOperator.getCodelinesFromCallable(self.mixinmethod)
        for target in self.configs.target:
            self.namespace = self.getNameSpace(target)
            cor = CodeOperator(
                self.mixin_getattr(target, self.method), debugmode=self.debugmode
            )
            self.mixin_setattr(
                target,
                self.method,
                self.rename_method(
                    self.doinsert(cor, cor.insertlines_end, codes).export(
                        self.namespace
                    ),
                    self.mixin_getattr(target, self.method),
                ),
            )

    def mixin_insert(self) -> None:
        codes = CodeOperator.getCodelinesFromCallable(self.mixinmethod)
        if self.insertline == None:
            self.mixin_head()
        if isinstance(self.poplines, int):
            self.poplines = [self.poplines]
        for target in self.configs.target:
            self.namespace = self.getNameSpace(target)
            cor = CodeOperator(
                self.mixin_getattr(target, self.method), debugmode=self.debugmode
            )
            self.mixin_setattr(
                target,
                self.method,
                self.rename_method(
                    self.doinsert(cor, cor.insertlines, self.insertline, codes).export(
                        self.namespace
                    ),
                    self.mixin_getattr(target, self.method),
                ),
            )

    def func_init(self, mixinmethod: Callable) -> Callable:
        self.mixinmethod = mixinmethod
        for cab in self.method:
            self.namespace = self.getNameSpace(cab)
            codes = CodeOperator.getCodelinesFromCallable(mixinmethod)
            cor = CodeOperator(cab, debugmode=self.debugmode)
            if self.at == At.INSERT:
                rebuild = self.rename_method(
                    self.doinsert(cor, cor.insertlines, self.insertline, codes).export(
                        self.namespace
                    ),
                    cab,
                )
            elif self.at == At.END:
                rebuild = self.rename_method(
                    self.doinsert(cor, cor.insertlines_end, codes).export(
                        self.namespace
                    ),
                    cab,
                )
            else:
                rebuild = self.rename_method(
                    self.doinsert(cor, cor.insertlines_head, codes).export(
                        self.namespace
                    ),
                    cab,
                )
            self.mixin_setattr(cab, "__code__", rebuild.__code__)
        return mixinmethod

    @staticmethod
    def withFunc(
        at: At,
        func: Union[Callable, List[Callable]],
        insertline: Union[None, int] = None,
        poplines: Union[int, List[int]] = [],
        insertfirst: bool = True,
        namespace: Dict[str, object] = {},
        debugmode: bool = False,
        gc: bool = False,
        mixintools: MixinTools = MixinTools(),
    ):
        if not isinstance(poplines, Iterable):
            poplines = [poplines]

        if not isinstance(func, Iterable):
            func = [func]

        return (
            Inject.cast(Inject, at, func, gc, mixintools)
            .addkwargs(
                insertline=insertline,
                poplines=poplines,
                insertfirst=insertfirst,
                namespace=namespace,
                debugmode=debugmode,
            )
            .func_init
        )

    @staticmethod
    def withValue(
        at: At,
        method: Union[str, MethodType, None] = None,
        insertline: Union[None, int] = None,
        poplines: Union[int, List[int]] = [],
        insertfirst: bool = True,
        namespace: NameSpace = NameSpace(),
        debugmode: bool = False,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ):
        if not isinstance(poplines, Iterable):
            poplines = [poplines]

        return (
            Inject.cast(Inject, at, method, gc, mixintools)
            .addkwargs(
                insertline=insertline,
                poplines=poplines,
                insertfirst=insertfirst,
                namespace=namespace,
                debugmode=debugmode,
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

@hasInstance
class ClassTracer:
    instance: Self
    tracelist: List[Type]

    def __init__(self) -> None:
        self.update()

    def update(self) -> Self:
        self.tracelist = object.__subclasses__()
        return self

    def fromName(self, part: str):
        return [t for t in self.tracelist if part in t.__name__]

    def fromNameFirst(self, part: str) -> Union[None, Type]:
        for t in self.tracelist:
            if part in t.__name__:
                return t

    def equalName(self, name: str) -> List[Type]:
        return [t for t in self.tracelist if name == t.__name__]

    def equalNameFirst(self, name: str) -> Union[None, Type]:
        for t in self.tracelist:
            if name == t.__name__:
                return t
