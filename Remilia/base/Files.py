from abc import ABC,abstractmethod

from ..LiteResource import Path, PathError


class CommonFileBase(ABC):
    def __init__(
        self,
        path:Path,
        noneText:str=""
        ) -> None:
        self.noneText=noneText
        self.encoding=path.encoding
        self.path=path
        if path.isexist:
            if path.text == "":
                with open(path.abspath,"w",encoding=self.encoding) as File:
                    File.write(noneText)
        else:
            with open(path.abspath,"w",encoding=self.encoding) as File:
                File.write(noneText)
    
    @abstractmethod
    def _read(
        self,
        *args,
        **kwargs,
        ) -> any:
        return any

    def read(
        self,
        *args,
        **kwargs) -> any:
        return self._read(...)
    
    @abstractmethod
    def read(
        self,
        *args,
        **kwargs
        ) -> any:
        return ...

    @abstractmethod
    def write(
        self,
        *args,
        **kwargs,
        ) -> None:
        return None
    
    def _build(self):
        self.path.write("w",self.noneText,self.encoding)
        return self
    
class MultFilesBase(ABC):
    def __init__(
        self,
        path:Path,
        structure=CommonFileBase
        ) -> None:
        self.path=path
        self.structure=structure
        if self.path.ISFILE:
            raise PathError("The target is not a Directory")
        if not self.path.isexist:
            self.path.buildDirectory()
    
    @abstractmethod
    def createFile(self,name):
        return self.structure(Path(self.path.abspath+"/"+name))._build()

    @abstractmethod
    def getFile(self,name):
        return self.structure(Path(self.path.abspath+"/"+name))
    
class KVFileBase(CommonFileBase):
    @property
    def Dict(self):
        return self._read()
    
    @abstractmethod
    def _read(self) -> dict:
        return {
            str:...,str:...
        }
    
    def read(
        self,
        key,
        ) -> None:
        return self._read(...)[key]
    
    @abstractmethod
    def write(
        self,
        key,
        value
        ) -> None:
        return None

class MultKVFiles(MultFilesBase):
    def __init__(
        self,
        path:Path,
        structure=KVFileBase
        ) -> None:
        super().__init__(path,structure)
    
    def swichto(self,name):
        if Path(self.path.abspath+"/"+name).isexist:
            pass
        else:
            raise PathError("No such file %s/%s"%(self.path.abspath,name))