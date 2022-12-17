from json import dumps, loads
from ..base.Files import KVFileBase
from .LiteResource import File


class JsonFile(KVFileBase):
    def __init__(self, File:File) -> None:
        super().__init__(File, r"{}")
    
    def _read(self,key):
        return loads(self.File.text)[key]
    
    @property
    def FileDict(self) -> dict:
        return loads(self.File.text)
    
    def _write(self, key, value,indent=4) -> None:
        kvdict=self.FileDict
        kvdict.update({key:value})
        self.File.write("w",
                        dumps(
                            kvdict,
                            indent=indent
                            )
                        )
        
class YamlFile(KVFileBase):
    def __init__(self, File:File,Loader=None) -> None:
        super().__init__(File, r"{}")
        if not Loader:
            from yaml import Loader as loader
            self.Loader=loader
        else:
            self.Loader=Loader
    def _read(self,key):
        from yaml import load
        return load(self.File.text,self.Loader)[key]
    
    @property
    def FileDict(self) -> dict:
        from yaml import load
        return load(self.File.text,self.Loader)
    
    def _write(self,key,value):
        from yaml import dump
        kvdict=self.FileDict
        kvdict.update({key:value})
        self.File.write("w",
                        dump(
                            kvdict,
                            )
                        )

