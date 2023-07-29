from types import MethodType
from typing import Generic, TypeVar

from typing_extensions import Self

RT=TypeVar("RT")
T=TypeVar("T")
NT=TypeVar("NT")
VT=TypeVar("VT")
class VarBuilder:
    def new(self,parents:tuple,custom_warp=None,init_args:tuple=(),init_kwargs:dict={}):
        return self.new_cls(parents=parents,custom_warp=custom_warp)(*init_args,**init_kwargs)
    
    def new_cls(self,parents:tuple,custom_warp=None):
        class cusVar(*parents):pass
        warp = self.warp if not custom_warp else custom_warp
        [setattr(cusVar,_,warp(getattr(cusVar,_))) for _ in dir(cusVar) if self.check(_)]
        return cusVar
    
    def check(self,attr):
        return not attr.startswith("__")
    
    def warp(self,warpin):
        def inner(*arg,**args):
            return warpin(*arg,**args)
        return inner
    
import json
import re


def typedet(string:str,strict=True) -> any:
    if not re.match(r"[\u4E00-\u9FA5A-Za-z]",string) and re.match(r"[0-9]",string) and not re.match(r"[`~!@#$%^&*()_\-+=<>?:\"{}|,\/;'\\[\]·~！@#￥%……&*（）——\-+={}|《》？：“”【】、；‘'，。、]",string):
        if "." in string:
            try:
                return float(string)
            except:
                pass
        else:
            return int(string)
    try:
        res=json.loads(string,strict=strict)
        return res
    except:
        pass
    return string

class Pair(Generic[NT,VT]):
    def __init__(self,name:NT,value:VT) -> None:
        self._name=name
        self._value=value
    
    def getname(self) -> NT:
        return self._name
    
    def getvalue(self) -> VT:
        return self._value
    
    @property
    def name(self) -> NT:
        return self.getname()
    
    @property
    def value(self) -> VT:
        return self.getvalue()
    
    @staticmethod
    def fromnv(name:NT,value:VT) -> Self:
        return Pair(name,value)