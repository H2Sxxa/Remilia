from json import dumps, loads
from .base.Files import KVFileBase
from .LiteResource import Path


class JsonConfig(KVFileBase):
    def __init__(self, path: Path) -> None:
        super().__init__(path, r"{}")
        
    def _read(self):
        return loads(self.path.text)
    
    def write(self, key, value,indent=4) -> None:
        kvdict=self._read()
        kvdict.update({key:value})
        self.path.write("w",
                        dumps(
                            kvdict,
                            indent=indent
                            )
                        )
        
class YamlConfig(KVFileBase):
    def __init__(self, path: Path) -> None:
        super().__init__(path, r"{}")
        
    def _read(self,Loader=None):
        from yaml import load
        if not Loader:
            from yaml import Loader
            aLoader=Loader
        else:
            aLoader=Loader
        return load(self.path.text,aLoader)
    
    def write(self,key,value,Loader=None):
        from yaml import dump,load
        if not Loader:
            from yaml import Loader
            kvdict=self._read(Loader=Loader)
        else:
            kvdict=self._read(Loader=Loader)
            
        kvdict.update({key:value})
        self.path.write("w",
                        dump(
                            kvdict,
                            )
                        )
        