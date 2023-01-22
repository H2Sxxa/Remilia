from abc import ABC,abstractmethod

from ..lite.LiteResource import File,Directory, PathError


class CommonFileBase(ABC):
    def __init__(
        self,
        File:File,
        noneText:str=""
        ) -> None:
        self.noneText=noneText
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