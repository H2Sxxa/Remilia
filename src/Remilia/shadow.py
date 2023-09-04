from types import MethodType
from typing import Any, Callable, Dict, List, Type, Union
from inspect import _empty
from uuid import uuid4

from .mixin import MixinBase, MixinTools
from .base.exceptions import ExistedObjectError, NoSuchMethodError
from .depi import Signs

SHADOW_MAP = "__shadowmethod_map__"

EmptyType = _empty


def getShadowWarpWithCls(cls):
    return Shadow.withCls(cls)


class Shadow(MixinBase):
    def mixin(self) -> None:
        for t_cls in self.configs.target:
            if not self.mixin_hasattr(t_cls, SHADOW_MAP):
                self.mixin_setattr(t_cls, SHADOW_MAP, dict())

            shadowmap: Dict[str, Dict[MethodType, List]]
            shadowmap = self.mixin_getattr(t_cls, SHADOW_MAP)
            if not shadowmap.__contains__(self.method):
                shadowmap.update({self.method: dict()})
                if self.mixin_hasattr(t_cls, self.method):
                    shadowmap.get(self.method).update(
                        {
                            self.mixin_getattr(
                                t_cls, self.method
                            ): Signs.getParasAsType(
                                self.mixin_getattr(t_cls, self.method)
                            )
                        }
                    )
            while True:
                tmpname = self.shadowName
                if not self.mixin_hasattr(t_cls, tmpname):
                    self.mixin_setattr(t_cls, tmpname, self.mixinmethod)
                    shadowmap.get(self.method).update(
                        {
                            self.mixin_getattr(t_cls, tmpname): Signs.getParasAsType(
                                self.mixinmethod
                            )
                        }
                    )
                    break

    @property
    def shadowName(self) -> str:
        return self.method + "_%s" % str(uuid4()).replace("-", "")

    @staticmethod
    def withValue(
        method: Union[str, MethodType, None] = None,
        gc: bool = None,
        mixintools: MixinTools = MixinTools(),
    ):
        return Shadow.cast(Shadow, None, method, gc, mixintools).init


class ShadowInvoker:
    def __init__(self, cls: Type) -> None:
        self.cls = cls

    def getShadowMap(self) -> Dict:
        return getattr(self.cls, SHADOW_MAP)

    def findAllWithType(self, paratype: List[object]) -> List[MethodType]:
        shadowmap: Dict[str, Dict[MethodType, List]]
        shadowmap = getattr(self.cls, SHADOW_MAP)
        result = []
        for nvmap in [v for _, v in shadowmap.items()]:
            result.extend([n for n, v in nvmap.items() if v == paratype])
        return result

    def findFirstWithType(self, paratype: List[object]) -> List[MethodType]:
        try:
            return self.findAllWithType(paratype)[0]
        except:
            raise NoSuchMethodError(
                "can't find method with %s in %s" % (paratype, self.cls)
            )

    def findAll(
        self, method: Union[str, MethodType], paratype: List[object]
    ) -> List[MethodType]:
        shadowmap: Dict[str, Dict[MethodType, List]]
        shadowmap = getattr(self.cls, SHADOW_MAP)
        if not issubclass(method.__class__, str):
            methodN = method.__name__
        else:
            methodN = method
        return [
            method for method, paras in shadowmap[methodN].items() if paras == paratype
        ]

    def findFirst(
        self, method: Union[str, MethodType], paratype: List[object]
    ) -> MethodType:
        try:
            return self.findAll(method, paratype)[0]
        except:
            raise NoSuchMethodError(
                "can't find '%s' method with %s in %s" % (method, paratype, self.cls)
            )

    def invokeAll(
        self, method: Union[str, MethodType], paratype: List[object], *args, **kwargs
    ) -> List[Any]:
        return [mtd(*args, **kwargs) for mtd in self.findAll(method, paratype)]

    def invokeFirst(
        self, method: Union[str, MethodType], paratype: List[object], *args, **kwargs
    ) -> Any:
        return self.findFirst(method, paratype)(*args, **kwargs)

    def invokeAllWithType(self, paratype: List[object], *args, **kwargs) -> List[Any]:
        return [mtd(*args, **kwargs) for mtd in self.findAllWithType(paratype)]

    def invokeFirstWithType(self, paratype: List[object], *args, **kwargs) -> Any:
        return self.findFirstWithType(paratype)(*args, **kwargs)


class ShadowAccessor:
    def __init__(self, cls: Type, force=False) -> None:
        self.cls = cls
        self.force = force

    def setAccessible(self, name: str, force=None) -> None:
        if force == None:
            force = self.force
        if not force:
            if hasattr(self.cls, name):
                raise ExistedObjectError(
                    "%s has existed object -> %s" % (self.cls.__name__, name)
                )
        setattr(
            self.cls, name, lambda _: getattr(_, "_%s%s" % (_.__class__.__name__, name))
        )
        setattr(self.cls, name, property(getattr(self.cls, name)))

    def Accessor(self, method: Callable):
        self.setAccessible(method.__name__)
