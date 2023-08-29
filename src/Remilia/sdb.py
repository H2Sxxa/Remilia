from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Union
from typing_extensions import Self
from yaml import Loader, Dumper, dump as ydump, load as yload
from json import loads as jloads, dumps as jdump

from Remilia.base.typings import T, NT, VT
from Remilia.res import rDir, rFile, rPath
from Remilia.fancy import hasInstance, LinkTun, toInstance
from Remilia.expression import exception, when


class EnumMode(Enum):
    AUTO = 0
    EXCEPTION = 1


class DataStructBase(ABC):
    """
    contains a specification of a DataStruct
    """

    instance: Self

    @abstractmethod
    def loads(self, data: str) -> Dict[str, T]:
        ...

    @abstractmethod
    def dumps(self, data: Dict[str, T]) -> str:
        ...

    @property
    def empty(self) -> str:
        return "{}"


@toInstance
@hasInstance
class YamlStruct(DataStructBase):
    loader: Loader
    dumper: Dumper

    def __init__(self, loader: Loader = Loader, dumper: Dumper = Dumper) -> None:
        super().__init__()
        self.loader = loader
        self.dumper = dumper

    def loads(self, data: str) -> Dict[str, T]:
        return yload(data, self.loader)

    def dumps(self, data: Dict[str, T]) -> str:
        return ydump(data, Dumper=self.dumper)


@toInstance
@hasInstance
class JsonStruct(DataStructBase):
    def loads(self, data: str) -> Dict[str, T]:
        return jloads(data)

    def dumps(self, data: Dict[str, T]) -> str:
        return jdump(data)


class DataBaseTable(LinkTun):
    def __init__(self, __file: Union[rFile, str], __struct: DataStructBase) -> None:
        self.__file = (
            __file.to_file() if isinstance(__file, rPath) else rPath(__file).to_file()
        )
        self.__struct = __struct
        when(not self.__file.exists(), lambda: self.__file.write(self.__struct.empty))

    def readValue(self, key: str) -> T:
        return self.read()[key]

    def read(self) -> Dict[str, T]:
        return self.__struct.loads(self.__file.text)

    def readValueElse(self, key: str, elsevalue: T) -> T:
        return self.readValue(key) if self.hasKey(key) else elsevalue

    def writeKVS(self, kvmap: Dict[str, T]) -> Self:
        _ = self.read()
        _.update(kvmap)
        self.write(_)
        return self

    def writeKV(self, key: NT, value: VT, /) -> Self:
        tmp = self.read()
        tmp.update({key: value})
        self.__file.write(self.__struct.dumps(tmp))
        return self

    def hasKey(self, key: T) -> bool:
        return self.read().__contains__(key)

    def write(self, data: Dict[str, T], mode: str = "w") -> Self:
        self.getFile().write(self.__struct.dumps(data), mode)
        return self

    def update(self, *__m: Dict[str, T]) -> Self:
        data = self.read()
        for i in __m:
            data.update(i)
        self.write(data)
        return self

    def __str__(self) -> str:
        return "%s[%s] <%s>" % (self.__class__.__name__, self.read(), self.name)

    def backto(self) -> "DataBaseCate":
        return super().backto()

    def getFile(self):
        return self.__file

    @property
    def name(self):
        return self.__file.name


class DataBaseCate(LinkTun):
    def __init__(
        self,
        catePath: Union[rDir, str],
        struct: DataStructBase,
        *,
        mode: EnumMode = EnumMode.AUTO,
    ) -> None:
        self.__dir = (
            catePath.to_dictory()
            if isinstance(catePath, rPath)
            else rPath(catePath).to_dictory()
        )
        self.__struct = struct
        self.__mode = mode
        self.__dir.makedirs()

    def createTable(self, name: str) -> DataBaseTable:
        return DataBaseTable("%s/%s" % (self.getDir(), name), self.__struct).setBack(
            self
        )

    def getTable(self, name: str) -> DataBaseTable:
        if self.__mode == EnumMode.EXCEPTION:
            when(
                not self.hasTable(name),
                lambda: exception(Exception("No such Table '%s'" % name)),
            )

        return DataBaseTable("%s/%s" % (self.getDir(), name), self.__struct).setBack(
            self
        )

    def hasTable(self, name: str) -> bool:
        return [] != [table for table in self.getTables() if table.name == name]

    def backto(self) -> "DataBase":
        return super().backto()

    def getTables(self) -> List[DataBaseTable]:
        return [
            DataBaseTable(rf.to_file()) for rf in self.__dir.glob("*") if rf.is_file()
        ]

    @property
    def name(self) -> str:
        return self.__dir.name

    def getDir(self) -> rDir:
        return self.__dir

    def __str__(self) -> str:
        return "%s[%s] <%s>" % (self.__class__.__name__, self.getTables(), self.name)


class DataBase:
    def __init__(
        self,
        rootPath: Union[rPath, str],
        struct: DataStructBase,
        *,
        mode: EnumMode = EnumMode.AUTO,
    ) -> None:
        self.__dir = (
            rootPath.to_dictory()
            if isinstance(rootPath, rPath)
            else rPath(rootPath).to_dictory()
        )
        self.__struct = struct.instance
        self.__mode = mode
        self.__dir.makedirs()

    def getCate(self, name: str) -> DataBaseCate:
        if self.__mode == EnumMode.EXCEPTION:
            when(
                not self.hasCate(name),
                lambda: exception(Exception("No such Cate '%s'" % name)),
            )
        return DataBaseCate(
            "%s/%s" % (self.getDir(), name), self.__struct, mode=self.__mode
        ).setBack(self)

    def getCates(self) -> List[DataBaseCate]:
        return [
            DataBaseCate(rd, self.__struct, mode=self.__mode).setBack(self)
            for rd in self.getDir().glob("*")
            if rd.is_dir()
        ]

    def hasCate(self, name: str) -> bool:
        return [] != [cate for cate in self.getCates() if cate.name == name]

    def createCate(self, name: str) -> DataBaseCate:
        return DataBaseCate("%s/%s" % (self.getDir(), name), self.__struct).setBack(
            self
        )

    @property
    def name(self):
        return self.getDir().name

    def getDir(self) -> rDir:
        return self.__dir

    def __str__(self) -> str:
        return "%s[%s] <%s>" % (self.__class__.__name__, self.getCates(), self.name)
