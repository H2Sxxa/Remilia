from functools import partial
import json,yaml
from typing import Callable, Dict, Union
from typing_extensions import Self
from abc import ABC,abstractmethod

from .res import rDir, rFile, rPath
from .base.rtypes import NT,VT

class DataStructBase(ABC):
    def createcate(self,root:rPath,name:str) -> "DataBase":
        return DataBase(rPath(root,name).to_dictory().makedirs(),self)
    
    def createfile(self,db:"DataBase",name:str) -> rFile:
        return rFile(db.root,name).write(self._initdata())
    
    def readkv(self,file:rFile,key:NT) -> VT:
        return self.readdict(file)[str(key)]
    
    def readdict(self,file:rFile) -> Dict[NT,VT]:
        return self._todict(file.text)
    
    def writekv(self,file:rFile,key:NT,value:VT) -> Self:
        return self.writedict(file,{key:value})
    
    def writedict(self,file:rFile,data:Dict[NT,VT]) -> Self:
        file.write(self._tostring(self.__updatedict(self.readdict(file),data)))
        return self
    
    def pop(self,file:rFile,key:NT) -> Self:
        data=self.readdict(file)
        data.pop(key)
        return self.writedict(file,data)
    
    def fastwrite(self,file:rFile,func:Callable[[Dict[NT,VT]],Dict[NT,VT]]) -> Self:
        return self.writedict(file,func(self.readdict(file)))
    
    def __updatedict(self,data:Dict[NT,VT],addons:Dict[NT,VT]):
        data.update(addons)
        return data
    
    @abstractmethod
    def _initdata(self) -> str:
        ...
    
    @abstractmethod
    def _todict(self,data:str) -> dict:
        ...
        
    @abstractmethod
    def _tostring(self,data:Dict[NT,VT]) -> str:
        ...

class JsonStruct(DataStructBase):
    def _initdata(self) -> str:
        return "{}"
    def _todict(self, data: str) -> dict:
        return json.loads(data)
    def _tostring(self, data: Dict[NT, VT]) -> str:
        return json.dumps(data,indent=4)

class YamlStruct(DataStructBase):
    def _initdata(self) -> str:
        return "{}"
    def _todict(self, data: str) -> dict:
        return yaml.load(data,Loader=yaml.Loader)
    def _tostring(self, data: Dict[NT, VT]) -> str:
        return yaml.dump(data,Dumper=yaml.Dumper)
    
class DataBase:
    def __init__(self,root:Union[rPath,rDir],struct:DataStructBase,auto_create_file:bool=True) -> None:
        self.root=root if isinstance(root,rPath) else rPath(root)
        self.struct=struct
        self.auto_create_file=auto_create_file
        self.root.to_dictory().makedirs()

    def get(self,name:str) -> rFile:
        if self.auto_create_file:
            return self.cget_file(name)
        else:
            return self.get_file(name)
        
    def get_file(self,name:str) -> rFile:
        rf=rFile(self.root,name)
        if rf.check():
            return rf
        else:
            raise FileExistsError("%s does't exist"%rf)
        
    def cget_file(self,name:str) -> rFile:
        rf=rFile(self.root,name)
        return rf if rf.check() else self.createfile(name)
    
    #struct
    def createcate(self,name:str) -> "DataBase":
        return self.struct.createcate(self.root,name)
    
    def createfile(self,name:str) -> rFile:
        return self.struct.createfile(self,name)
    
    def readkv(self,name:str,key:NT) -> VT:
        return self.struct.readkv(self.get_file(name),key)
    
    def readdict(self,name:str) -> Dict[NT,VT]:
        return self.struct.readdict(self.get(name))
    
    def writekv(self,name:str,key:NT,value:VT) -> Self:
        return self.struct.writekv(self.get(name),key,value)
    
    def writedict(self,name:str,data:Dict[NT,VT]) -> Self:
        self.struct.writedict(self.get(name),data)
        return self
    
    def pop(self,name:str,key:NT) -> Self:
        self.struct.pop(self.get(name),key)
        return self
    
    def fastwrite(self,name:str,func:Callable[[Dict[NT,VT]],Dict[NT,VT]]) -> Self:
        self.struct.fastwrite(self.get(name),func)
        return self