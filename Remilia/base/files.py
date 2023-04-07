from abc import ABC,abstractmethod

from ..lite.LiteResource import Directory, PathError

from ..lite.LiteResource import File as FileType
class CommonFileBase(ABC):
    def __init__(
        self,
        File:FileType,
        noneText:str=""
        ) -> None:
        self.noneText=noneText
        
        if isinstance(File,FileType):
            File=FileType(File)
        
        self.File=File
        if not File.isexist or File.text == "":
            File.write("w",noneText)
    
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
        **kwargs
        ) -> any:
        return self._read(*args,**kwargs)
    
    @abstractmethod
    def _write(
        self,
        *args,
        **kwargs,
        ) -> None:
        return None

    def write(
        self,
        *args,
        **kwargs,
        ) -> None:
        return self._write(*args,**kwargs)
    
class KVFileBase(CommonFileBase):
    @abstractmethod
    def FileDict(self) -> dict:
        return {}
    
    @abstractmethod
    def _read(
        self,
        key,
        ) -> dict:
        return {
            str:...,str:...
        }
    
    def read(
        self,
        key,
        *args,
        **kwargs,
        ) -> any:
        return self._read(
            key,
            *args,
            **kwargs,
            )
    
    @abstractmethod
    def _write(
        self,
        key,
        value,
        ) -> None:
        return None
    
    def write(
        self,
        key:str,
        value,
        *args,
        **kwargs,
        ) -> None:
        return self._write(
            key,
            value,
            *args,
            **kwargs,
            )