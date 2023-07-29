from abc import ABC,abstractmethod
from enum import Enum
from types import MethodType
from typing import Any, List, Type, Union
from typing_extensions import Self

class At(Enum):
    BEFORE_INVOKE = -1
    INVOKE = 0
    HEAD = 1
    RETURN = 2
    AFTER_RETURN = 3

MIXIN_TARGETSCLS="__mixin_targetcls__"


class Mixin:
    target:List[Type]
    debuginfo:List[Exception]
    
    def __init__(self, target: List[Type]) -> None:
        self.target=target
        self.debuginfo=[]
    def __call__(self,mixincls:Type) -> Any:
        for mname in dir(mixincls):
            try:
                obj=getattr(mixincls,mname)
                if isinstance(obj,MethodType):
                    setattr(obj,MIXIN_TARGETSCLS,self.target)
            except Exception as e:
                self.debuginfo.append(e)
                
class MixinMethodType("MethodType"):
    @property
    def __mixin_targetcls__(self) -> Type:
        return None
class MixinBase(ABC):
    at:At
    method:str
    
    
    def init(self,mixinmethod:MethodType):
        if self.method == None:
            self.method=mixinmethod.__name__
        elif isinstance(self.method,str):
            pass
        else:
            self.method=self.method.__name__
    
    def cast(self,subtype:"MixinBase",at:At,method:Union[str,MethodType,None]=None) -> MethodType:
        return subtype().new(at,method).init
    
    def new(self,at:At,method:Union[str,MethodType,None]=None) -> Self:
        self.at=at
        self.method=method        
        return self
    
    @abstractmethod
    @staticmethod
    def withValue(at:At,method:Union[str,MethodType,None]=None):
        '''
        if method == None,it will pick up the name of the MixinMethod
        '''
        return MixinBase().cast(MixinBase,at,method)

class Inject(MixinBase):pass

class Redirect(MixinBase):
    pass


class OverWrite(MixinBase):
    pass
