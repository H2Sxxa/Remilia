from pathlib import Path as _Path
from typing import Dict, List, Optional, Sequence, Union
from typing_extensions import Self
from os import path as opath
from os import makedirs, mkdir

from .base.typings import T
from .base.models import PathTimes, SizeUnits


class NotFoundError(OSError):
    pass


class DirectoryNotFoundError(OSError):
    pass


def format_size(size: int, unit: SizeUnits = SizeUnits()):
    if size < 1024:
        return (round(size, 2), unit.BYTES)
    else:
        KBX = size / 1024
        if KBX < 1024:
            return (round(KBX, 2), unit.K)
        else:
            MBX = KBX / 1024
            if MBX < 1024:
                return (round(MBX, 2), unit.M)
            else:
                return (round(MBX / 1024), unit.G)


class rPath(type(_Path()), _Path):
    def __init__(self, *args: str, **kwargs: Optional[Dict[str, T]]) -> None:
        super().__init__()
        self._args = args
        self._kwargs = kwargs

    def to_string(self) -> str:
        return str(self)

    def to_file(self) -> "rFile":
        return rFile(self)

    def to_dictory(self) -> "rDir":
        return rDir(self)

    def to_path(self) -> "rPath":
        return rPath(self)

    def convey(self) -> Union["rFile", "rDir"]:
        if not self.exists():
            raise NotFoundError(
                "%s is not existed,can't convey a unexisted rPath" % self
            )
        if self.is_dir():
            return rDir(self)
        else:
            return rFile(self)

    @property
    def times(self) -> PathTimes:
        return PathTimes(
            createtime=opath.getctime(self.absolute()),
            modifytime=opath.getmtime(self.absolute()),
            accesstime=opath.getatime(self.absolute()),
        )


class rFile(rPath):
    def __init__(self, *args: str, **kwargs: Optional[Dict[str, T]]) -> None:
        super().__init__(*args, **kwargs)
        self.encoding = "utf-8"

    def set_encoding(self, encoding="utf-8") -> Self:
        self.encoding = encoding
        return self

    def check(self) -> bool:
        return self.exists() and self.is_file()

    def read_text(self, errors: Union[str, None] = None) -> str:
        return super().read_text(self.encoding, errors)

    def write(
        self, data: T = "", mode: str = "w", has_encoding: bool = True, *args, **kwargs
    ) -> Self:
        if has_encoding:
            with self.open(mode=mode, encoding=self.encoding, *args, **kwargs) as f:
                f.write(data)
        else:
            with self.open(mode=mode, *args, **kwargs) as f:
                f.write(data)
        return self

    def read(self, mode: str = "r", *args, **kwargs) -> Union[str, bytes]:
        with self.open(mode=mode, encoding=self.encoding, *args, **kwargs) as f:
            return f.read()

    @property
    def bytes(self):
        return self.read_bytes()

    @property
    def text(self):
        return self.read_text()

    @property
    def parent(self: Self) -> "rDir":
        return rPath(self).parent.to_dictory()

    @property
    def parents(self: Self) -> Sequence["rDir"]:
        return [rDir(rp) for rp in rPath(self).parents]

    @property
    def size(self) -> int:
        return opath.getsize(self.absolute())

    def fsize(self, unit: SizeUnits = SizeUnits()) -> str:
        return format_size(self.size, unit)

    @property
    def exts(self) -> List[str]:
        result = []
        tempPath = self.absolute()
        lastTemp = ""
        while len(opath.splitext(tempPath)) > 1:
            handle = opath.splitext(tempPath)
            if lastTemp == handle[0]:
                break
            else:
                lastTemp = handle[0]
            result.append(handle[-1])
            tempPath = handle[0]
        result.reverse()
        return result

    @property
    def ext(self) -> str:
        return opath.splitext(self)[-1]


class rDir(rPath):
    def check(self) -> bool:
        return self.exists() and self.is_dir()

    def size(self, pattern: str = "*"):
        return sum([rFile(rp).size for rp in rPath(self).glob(pattern) if rp.is_file()])

    def rsize(self, pattern: str = "*"):
        return sum(
            [rFile(rp).size for rp in rPath(self).rglob(pattern) if rp.is_file()]
        )

    def fsize(self, pattern: str = "*", unit: SizeUnits = SizeUnits()) -> str:
        return format_size(self.size(pattern), unit)

    def frsize(self, pattern: str = "*", unit: SizeUnits = SizeUnits()) -> str:
        return format_size(self.rsize(pattern), unit)

    def makedirs(self, exist_ok=True, *args, **kwargs) -> Self:
        makedirs(self.absolute(), exist_ok=exist_ok, *args, **kwargs)
        return self

    def mkdir(self, *args, **kwargs) -> Self:
        mkdir(self.absolute(), *args, **kwargs)
        return self

    def newFile(self, name: str, contant: Union[str, bytes], *args, **kwargs):
        return rFile("%s/%s" % (self.absolute().to_string(), name)).write(
            contant, *args, **kwargs
        )


class DirBuilder:
    root: rDir

    def __init__(self, root: Union[rDir, str] = rDir("")) -> None:
        self.root = root

    def forward(self, name: str) -> "DirBuilder":
        return DirBuilder(rDir(self.root, name).makedirs())

    def back(self) -> "DirBuilder":
        return DirBuilder(self.root.parent.to_dictory().makedirs())

    @property
    def pback(self) -> "DirBuilder":
        return DirBuilder(self.root.parent.to_dictory().makedirs())

    def create_dir(self, name: str) -> Self:
        rDir(self.root, name).makedirs()
        return self

    def create_file(self, name: str, data: str) -> Self:
        rFile(self.root, name).write(data)
        return self
