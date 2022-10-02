from abc import ABC,abstractmethod
from ..LiteResource import Path


class CommonFileBase(ABC):
    @abstractmethod
    def read(
        self,
        *args,
        **kwargs,
        ) -> None:
        return any

    @abstractmethod
    def write(
        self,
        *args,
        **kwargs,
        ) -> None:
        return None
    

class KVFileBase(CommonFileBase):
    def __init__(
        self,
        path:Path,
        ) -> None:
        self.encoding=path.encoding
        if path.isexist:
            if path.text == "":
                with open(path.abspath,"w",encoding=self.encoding) as File:
                    File.write(r"{}")
        else:
            with open(path.abspath,"w",encoding=self.encoding) as File:
                File.write(r"{}")
        self.path=path
        
    @abstractmethod
    def read(
        self,
        key,
        ) -> None:
        return any

    @abstractmethod
    def write(
        self,
        key,
        value
        ) -> None:
        return None
    