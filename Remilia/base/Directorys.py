from abc import ABC

from ..lite.LiteResource import File,Directory, PathError

class CommonDirectorysBase(ABC):
    def __init__(
        self,
        directory:Directory,
        ) -> None:
        self.directory=directory
            
    def _getFile(path:str) -> File:
        return ...