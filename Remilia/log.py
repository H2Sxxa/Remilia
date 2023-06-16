from functools import partial
from colorama import Fore, Back, Style, Cursor
from colorama import init as initcolor
from typing import Dict, Optional,TYPE_CHECKING
from typing_extensions import Self
from pydantic import BaseModel
from sys import stdout
from time import strftime,localtime
from .base.rtypes import RT,T
from platform import system
import inspect

if TYPE_CHECKING:
    class _CallMethod:
        def __call__(self, *args: str) -> None:
            ...


try:
    if system() == "Windows":
        initcolor(wrap=True)
    else:
        initcolor(wrap=False)
except:
    pass

class Ruler(BaseModel):
    '''
    self -> Type(Log)
    '''
    level:int=5
    colors:dict={}
    excolor:str="fore.LIGHTGREEN_EX+'[ '+name+' '+time+' '+location+'] '+style.RESET_ALL+text"
    explain:str="'[ '+name+' '+time+' '+location+'] '+text"
    timeformat:str="%H:%M:%S"
    def exgenerate(self,model:str,*color:str) -> Self:
        self.explain=model % tuple(["" for _ in color])
        self.excolor=model % color
        return self
class Log:
    def __init__(self,name:str,logs:tuple=(),level:int=5) -> None:
        super().__init__()
        self.level=level
        self.logs=logs
        self.name=name.upper()
        
    def color(self,ruler:Ruler,location:str) -> str:
        #colorama stuff
        fore=Fore
        style=Style
        cursor=Cursor
        back=Back
        #base
        name=self.name
        text=" ".join(self.logs)
        time=strftime(
            ruler.timeformat,
            localtime()
            )
        __all__=[location,name,text,time,fore,style,cursor,back]
        return eval(ruler.excolor)
    
    def plain(self,ruler:Ruler,location:str) -> str:
        name=self.name
        text=" ".join(self.logs)
        time=strftime(
            ruler.timeformat,
            localtime()
            )
        __all__=[location,name,text,time]
        return eval(ruler.explain)

#TODO WRITE IT
class LogCat:
    def __init__(self) -> None:
        pass
        
class Logger:
    def __init__(self,logcat:LogCat=LogCat(),ruler_map:Optional[Dict[str,Ruler]]={},model:str="'%s[ '+name+' '+time+' '+location+'] %s'+text") -> None:
        self.ruler_map={
            "DEBUG":Ruler(level=3).exgenerate(model,Fore.CYAN,Style.RESET_ALL),
            "INFO":Ruler(level=5).exgenerate(model,Fore.LIGHTGREEN_EX,Style.RESET_ALL),
            "WARN":Ruler(level=6).exgenerate(model,Fore.LIGHTYELLOW_EX,Style.RESET_ALL),
            "ERROR":Ruler(level=7).exgenerate(model,Fore.LIGHTRED_EX,Style.RESET_ALL),
        }
        self.ruler_map.update(ruler_map)
        self.handle_out=print

        global instance
        instance=self
    
    def to_ruler(self,name:str,level:int) -> Self:
        self.ruler_map.update({name.upper():level})
        return self
    
    def get_ruler(self,name:str) -> Ruler:
        try:
            return self.ruler_map[name.upper()]
        except:
            return Ruler()
    def print(self,name:str,*log:Log) -> None:
        location=inspect.getmodule(inspect.stack()[1][0]).__name__
        level= 5 if name.upper() not in self.ruler_map.keys() else self.ruler_map[name.upper()]
        
        self.handle_out(Log(name,log,level).color(self.get_ruler(name),location))
        
    
    def __getattr__(self,name) -> "_CallMethod":
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        return partial(self.print,name)

instance:Logger = None
def get_logger(*args,**kwargs) -> Logger:
    '''
    args & kwargs only work under (instance == None)
    '''
    global instance
    if instance != None:
        return instance
    else:
        instance=Logger(*args,**kwargs)
        return instance
