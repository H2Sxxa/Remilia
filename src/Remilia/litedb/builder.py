import json,yaml
from typing import Callable, Dict, Union
from typing_extensions import Self
from abc import ABC,abstractmethod

from ..res import rDir, rFile, rPath
from ..base.rtypes import NT,VT

class DataStructBase(ABC):
    def createcate(self,root:rPath,name:str) -> "DataBase":
        return DataBase(rPath(root,name).to_dictory().makedirs(),self)
    
    def createfile(self,db:"DataBase",name:str) -> rFile:
        return rFile(db.root,name).write(self.initdata())
    
    def readkv(self,file:rFile,key:NT) -> VT:
        return self.readdict(file)[str(key)]
    
    def readdict(self,file:rFile) -> Dict[NT,VT]:
        return self.todict(file.text)
    
    def writekv(self,file:rFile,key:NT,value:VT) -> Self:
        return self.writedict(file,{key:value})
    
    def writedict(self,file:rFile,data:Dict[NT,VT]) -> Self:
        file.write(self.tostring(self.readdict(file).update(data)))
        return self
    
    def pop(self,file:rFile,key:NT) -> Self:
        data=self.readdict(file)
        data.pop(key)
        return self.writedict(file,data)
    
    def fastwrite(self,file:rFile,func:Callable[[Dict[NT,VT]],Dict[NT,VT]]) -> Self:
        return self.writedict(file,func(self.readdict(file)))
    
    @abstractmethod
    def initdata(self) -> str:
        ...
    
    @abstractmethod
    def todict(self,data:str) -> dict:
        ...
        
    @abstractmethod
    def tostring(self,data:Dict[NT,VT]) -> str:
        ...

class JsonStruct(DataStructBase):
    def initdata(self) -> str:
        return "{}"
    def todict(self, data: str) -> dict:
        return json.loads(data)
    def tostring(self, data: Dict[NT, VT]) -> str:
        return json.dumps(data,indent=4)

class YamlStruct(DataStructBase):
    def initdata(self) -> str:
        return "{}"
    def todict(self, data: str) -> dict:
        return yaml.load(data,Loader=yaml.Loader)
    def tostring(self, data: Dict[NT, VT]) -> str:
        return yaml.dump(data,Dumper=yaml.Dumper)
    
class DataBase:
    def __init__(self,root:Union[rPath,rDir],struct:DataStructBase) -> None:
        self.root=root
        self.struct=struct
        root.to_dictory().makedirs()
    
    