from json import dumps, loads
from .base.Files import KVFileBase
from .LiteResource import Path


class JsonConfig(KVFileBase):
    def read(self,key):
        return loads(self.path.text)[key]
    
    def write(self, key, value,indent=4) -> None:
        kvdict=loads(self.path.text)
        kvdict.update({key:value})
        self.path.write("w",
                        dumps(
                            kvdict,
                            indent=indent
                            )
                        )