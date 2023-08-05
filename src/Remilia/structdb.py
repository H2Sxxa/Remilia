import json
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Union

import yaml
from typing_extensions import Self

from .base.typings import NT, VT
from .res import DirectoryNotFoundError, rDir, rFile, rPath


class DataStructBase(ABC):
    def readkv(self,file:rFile,key:NT) -> VT:
        return self.readdict(file)[str(key)]
    
    def readdict(self,file:rFile) -> Dict[NT,VT]:
        return self._todict(file.text)
    
    def writekv(self,file:rFile,key:NT,value:VT) -> Self:
        return self.writedict(file,{key:value})
    
    def writedict(self,file:rFile,data:Dict[NT,VT]) -> Self:
        file.write(self._tostring(self.__updatedict(self.readdict(file),data)))
        return self
    
    def popkv(self,file:rFile,key:NT) -> Self:
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
    def __init__(self,root:Union[rPath,rDir],struct:DataStructBase,auto_create:bool=True) -> None:
        self.root=root if isinstance(root,rPath) else rPath(root)
        try:
            if issubclass(struct,DataStructBase):
                self.struct=struct if isinstance(struct,DataStructBase) else struct()
            else:
                self.struct=struct
        except:
            self.struct=struct
        self.auto_create=auto_create
        self.root.to_dictory().makedirs()
    
    def getf(self,name:str) -> rFile:
        if self.auto_create:
            return self.cget_file(name)
        else:
            return self.get_file(name)
    
    def getc(self,name:str) -> "DataBase":
        if self.auto_create:
            return self.cget_cate(name)
        else:
            return self.get_cate(name)
    
    def get_file(self,name:str) -> rFile:
        rf=rFile(self.root,name)
        if rf.check():
            return rf
        else:
            raise FileNotFoundError("%s does't exist"%rf)

    
    
    def get_cate(self,name:str) -> "DataBase":
        rf=rDir(self.root,name)
        if rf.check():
            return DataBase(rf,self.struct,self.auto_create)
        else:
            raise DirectoryNotFoundError("%s does't exist"%rf)

    def cget_file(self,name:str) -> rFile:
        rf=rFile(self.root,name)
        return rf if rf.check() else self.createfile(name)

    def cget_cate(self,name:str) -> "DataBase":
        rf=rDir(self.root,name)
        return DataBase(rf,self.struct,self.auto_create) if rf.check() else self.createcate(name)

    def createcate(self,name:str) -> "DataBase":
        return DataBase(rPath(self.root,name).to_dictory().makedirs(),self.struct,self.auto_create)
    
    def createfile(self,name:str) -> rFile:
        return rFile(self.root,name).write(self.struct._initdata())

    def get_all(self) -> List[Union["DataBase",rFile]]:
        return [rp.to_file() if rp.to_file().check() else DataBase(rp,self.struct,self.auto_create) for rp in self.root.glob("*")]
    
    def get_dbsf(self,name:str) -> "DBSubFile":
        return DBSubFile(self.getf(name),self)
    
    #struct
    def readkv(self,name:str,key:NT) -> VT:
        return self.struct.readkv(self.getf(name),key)
    
    def readdict(self,name:str) -> Dict[NT,VT]:
        return self.struct.readdict(self.getf(name))
    
    def writekv(self,name:str,key:NT,value:VT) -> Self:
        return self.struct.writekv(self.getf(name),key,value)
    
    def writedict(self,name:str,data:Dict[NT,VT]) -> Self:
        self.struct.writedict(self.getf(name),data)
        return self
    
    def popkv(self,name:str,key:NT) -> Self:
        self.struct.popkv(self.getf(name),key)
        return self
    
    def fastwrite(self,name:str,func:Callable[[Dict[NT,VT]],Dict[NT,VT]]) -> Self:
        self.struct.fastwrite(self.getf(name),func)
        return self
    
    #magic
    def __str__(self) -> str:
        return self.root.to_string()
    
    def __repr__(self) -> str:
        return "DataBase('%s')" % self.root

class DBSubFile:
    def __init__(self,file:rFile,db:DataBase) -> None:
        self.db=db
        self.file=file
        
    def writekv(self,key:NT,value:VT) -> Self:
        self.db.writekv(self.file.name,key,value)
        return self
    
    def writedict(self,data:Dict[NT,VT]) -> Self:
        self.db.writedict(self.file.name,data)
        return self
    
    def popkv(self,key:NT) -> Self:
        self.db.popkv(self.file.name,key)
        return self
    
    def fastwrite(self,func:Callable[[Dict[NT,VT]],Dict[NT,VT]]) -> Self:
        self.db.fastwrite(self.file.name,func)
        return self
    
    def readkv(self,key:NT) -> VT:
        return self.db.readkv(self.file.name,key)
    
    def readdict(self) -> Dict[NT,VT]:
        return self.db.readdict(self.file.name)
