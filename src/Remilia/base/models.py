from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Type, Union
from pydantic import BaseModel
from typing_extensions import Self

from Remilia.base.typings import T


class Ruler(BaseModel):
    """
    self -> Type(Log)
    """

    level: int = 5
    excolor: str = (
        "fore.LIGHTGREEN_EX+'[ '+name+' '+time+' '+location+'] '+style.RESET_ALL+text"
    )
    explain: str = "'[ '+name+' '+time+' '+location+'] '+text"
    timeformat: str = "%H:%M:%S"

    def exgenerate(self, model: str, *color: str) -> Self:
        self.explain = model % tuple(["" for _ in color])
        self.excolor = model % color
        return self


class PathTimes(BaseModel):
    createtime: float
    modifytime: float
    accesstime: float


class SizeUnits(BaseModel):
    BYTES: str = "Bytes"
    K: str = "K"
    M: str = "M"
    G: str = "G"


@dataclass
class Args:
    args = ()
    kwargs = {}

    def __init__(self, *args: T, **kwargs: T) -> None:
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return "Args[ *%s & **%s ]" % (self.args, self.kwargs)

    def appendArgs(
        self,
        *args: T,
    ) -> Self:
        self.args = (*self.args, *args)
        return self

    def appendKwargs(
        self,
        **kwargs,
    ) -> Self:
        self.kwargs.update(kwargs)
        return self


@dataclass
class SingleArg:
    arg_name: str
    arg_type: Type[T]
    arg_default: Optional[T]
    arg_index: Optional[int]
