from pathlib import Path as _Path
from typing import Dict, List, Optional, Sequence, Union
from typing_extensions import Self
from os import path as opath

from .base.rtypes import T
from .base.models import PathTimes
class rPath(type(_Path()),_Path):
    def __init__(self,*args:str,**kwargs:Optional[Dict[str,T]]) -> None:
        super().__init__()
        self._args=args
        self._kwargs=kwargs
    def to_file(self) -> "rFile":
        return rFile(self)
    def to_dictory(self) -> "rDir":
        return rDir(self)
    def convey(self) -> Union["rFile","rDir"]:
        if self.is_dir():
            return rDir(self)
        else:
            return rFile(self)
    @property
    def times(self) -> PathTimes:
        return PathTimes(
            createtime=opath.getctime(self.absolute()),
            modifytime=opath.getmtime(self.absolute()),
            accesstime=opath.getatime(self.absolute())
        )
        
class rFile(rPath):
    def __init__(self, *args: str, **kwargs: Optional[Dict[str, T]]) -> None:
        if self.is_dir():
            raise TypeError("'%s' is not a file" % self.absolute())
        super().__init__(*args, **kwargs)
        self.encoding='utf-8'
        
    def read_text(self, errors: Union[str,None]=None) -> str:
        return super().read_text(self.encoding, errors)
    
    def write(self,data:T="",mode:str="w",*args,**kwargs) -> None:
        with self.open(mode=mode,encoding=self.encoding,*args,**kwargs) as f:
            return f.write(data)
    def read(self,mode:str="r",*args,**kwargs) -> Union[str,bytes]:
        with self.open(mode=mode,encoding=self.encoding,*args,**kwargs) as f:
            return f.read()
    @property
    def bytes(self):
        return self.read_bytes()
    @property
    def text(self):
        return self.read_text()
    @property
    def parent(self: Self) -> "rDir":
        return rPath(self).parent.to_dictory()
    @property
    def parents(self: Self) -> Sequence["rDir"]:
        return map(rDir,rPath(self).parents)
    
    @property
    def size(self) -> int:
        return opath.getsize(self.absolute())
    
    @property
    def exts(self) -> List[str]:
        result=[]
        tempPath=self.absolute()
        lastTemp=""
        while len(opath.splitext(tempPath)) > 1:
            handle=opath.splitext(tempPath)
            if lastTemp == handle[0]:
                break
            else:
                lastTemp=handle[0]
            result.append(handle[-1])
            tempPath=handle[0]
        result.reverse()
        return result

    @property
    def ext(self) -> str:
        return opath.splitext(self)[-1]
    
class rDir(rPath):
    def __init__(self, *args: str, **kwargs: Optional[Dict[str, T]]) -> None:
        if not self.is_dir():
            raise TypeError("'%s' is not a dir" % self.absolute())
        super().__init__(*args, **kwargs)