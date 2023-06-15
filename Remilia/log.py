from functools import partial
from typing import Self
from .base.rtypes import RT

class Log(str):
    def __init__(self,name:str,logs:tuple=(),level:int=5) -> None:
        super().__init__()
        self.level=level
        self.logs=logs
        self.name=name
        
    def color(self) -> str:pass
    def plain(self) -> str:pass
    def sub(self) -> str:pass
    
    
class Render:
    def __init__(self) -> None:
        pass
    def render(self):pass
    def color_ruler(self) -> dict:pass


class Logger:
    def __init__(self,render:Render,level_map:dict={}) -> None:
        self.level_map={}
    
    def tolevel_map(self,name:str,level:int) -> Self:
        self.level_map.update({name.upper():level})
        return self
    
    def print(self,name:str,*log:Log) -> None:
        level= 5 if name.upper() not in self.level_map.keys() else self.level_map[name.upper()]
        Log(name,log,level)
    
    def __getattr__(self,name) -> None:
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        return partial(self.print,name)