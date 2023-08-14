from abc import ABC, abstractmethod
from typing import Dict, List
from typing_extensions import Self
from yaml import Loader, Dumper, dump as ydump, load as yload
from json import loads as jloads, dumps as jdump

from Remilia.base.typings import T, NT, VT
from Remilia.res import rDir, rFile, rPath
from Remilia.fancy import hasInstance, propertyOf, LinkTun, toInstance


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
    def __init__(self, __file: rFile, __struct: DataStructBase) -> None:
        self.__file = __file
        self.__struct = __struct

    def getValue(self, key: str) -> T:
        return self.read()[key]

    def read(self) -> Dict[str, T]:
        return self.__struct.loads(self.__file.text)

    def write(self, key: NT, value: VT, /) -> Self:
        tmp = self.read()
        tmp.update({key: value})
        self.__file.write(self.__struct.dumps(tmp))
        return self

    def __str__(self) -> str:
        return "%s[%s]" % (self.__class__.__name__, self.read())

    def backto(self) -> "DataBaseCate":
        return super().backto()


class DataBaseCate(LinkTun):
    def __init__(self, __dir: rDir, __struct: DataStructBase) -> None:
        self.__dir = (
            __dir.to_dictory()
            if isinstance(__dir, rPath)
            else rPath(__dir).to_dictory()
        )
        self.__dir.makedirs()
        self.__struct = __struct

    def createTable(self, name: str) -> DataBaseTable:
        return DataBaseTable(
            self.__dir.newFile(name, self.__struct.empty), self.__struct
        ).setBack(self)

    def hasTable(self, name: str):
        ...

    def backto(self) -> "DataBase":
        return super().backto()

    def getTables(self):
        ...

    def __str__(self) -> str:
        return super().__str__()


class DataBase:
    def __init__(
        self,
        rootPath: rPath,
        __struct: DataStructBase,
    ) -> None:
        self.rootPath = rootPath if isinstance(rootPath, rPath) else rPath(rootPath)
        self.__struct = __struct.instance

    def getRootDir(self) -> rDir:
        return self.rootPath.to_dictory()

    def getCate(self, name: str) -> DataBaseCate:
        return DataBaseCate("%s/%s" % (self.rootdir, name), self.__struct).setBack(self)

    def getCates(self) -> List[DataBaseCate]:
        return [
            DataBaseCate(i, self.__struct).setBack(self)
            for i in self.getRootDir().glob("*")
            if i.is_dir()
        ]

    def hasCate(self):...
    
    @propertyOf(getRootDir)
    def rootdir(self) -> rDir:
        ...

    def __str__(self) -> str:
        return "%s[%s]" % (self.__class__.__name__, self.getCates())
