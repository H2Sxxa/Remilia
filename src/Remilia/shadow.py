from types import MethodType
from typing import Any, Callable, Dict, List, Type, Union
from inspect import _empty
from uuid import uuid4

from Remilia.base.exceptions import NoSuchMethodError

from .signs import Signs


SelfType=_empty

def getShadowWarpWithCls(cls):
    return Shadow.withCls(cls)

class Shadow:
    def init(self, method: MethodType) -> MethodType:
        self.name = method.__name__
        self.method = method
        self.shadowUpdate()
        return method
    
    @staticmethod
    def withCls(cls:Type) -> Callable[[Type],Callable[[MethodType],MethodType]]:
        return Shadow()._withCls(cls)

    def _withCls(self,cls:Type) -> Callable[[MethodType],MethodType]:
        self.cls=cls
        return self.init
    
    @property
    def shadowName(self) -> str:
        return self.name + "_%s" % str(uuid4()).replace("-","")

    def shadowUpdate(self) -> None:
        if not hasattr(self.cls, "__shadowmethod_map__"):
            setattr(self.cls, "__shadowmethod_map__", dict())

        shadowmap: Dict[str, Dict[MethodType, List]]
        shadowmap = getattr(self.cls, "__shadowmethod_map__")
        if not shadowmap.__contains__(self.name):
            shadowmap.update({self.name: dict()})
        while True:
            tmpname=self.shadowName
            if not shadowmap.get(self.name).__contains__(tmpname):
                setattr(self.cls,tmpname,self.method)
                shadowmap[self.name].update({getattr(self.cls,tmpname):Signs.getParasAsType(self.method)})
                break

class ShadowInvoker:
    def __init__(self,cls:Type) -> None:
        self.cls=cls
    def findAllWithType(self,paratype:List[object]) -> List[MethodType]:
        shadowmap: Dict[str, Dict[MethodType, List]]
        shadowmap = getattr(self.cls, "__shadowmethod_map__")
        result=[]
        for nvmap in [v for _,v in shadowmap.items()]:
            result.extend([n for n,v in nvmap.items() if v == paratype])
        return result
    
    def findFirstWithType(self,paratype:List[object]) -> List[MethodType]:
        try:
            return self.findAllWithType(paratype)[0]
        except:
            raise NoSuchMethodError("can't find method with %s in %s"%(paratype,self.cls))   
                 
    def findAll(self,method:Union[str,MethodType],paratype:List[object]) -> List[MethodType]:
        shadowmap: Dict[str, Dict[MethodType, List]]
        shadowmap = getattr(self.cls, "__shadowmethod_map__")
        if not issubclass(method.__class__,str):
            methodN=method.__name__
        else:
            methodN=method
        return [method for method,paras in shadowmap[methodN].items() if paras == paratype]
        
    def findFirst(self,method:Union[str,MethodType],paratype:List[object]) -> MethodType:
        try:
            return self.findAll(method,paratype)[0]
        except:
            raise NoSuchMethodError("can't find '%s' method with %s in %s"%(method,paratype,self.cls))
        
    def invokeAll(self,method:Union[str,MethodType],paratype:List[object],*args,**kwargs) -> List[Any]:
        return [mtd(*args,**kwargs) for mtd in self.findAll(method,paratype)]

    def invokeFirst(self,method:Union[str,MethodType],paratype:List[object],*args,**kwargs) -> Any:
        return self.findFirst(method,paratype)(*args,**kwargs)

    def invokeAllWithType(self,paratype:List[object],*args,**kwargs) -> List[Any]:
        return [mtd(*args,**kwargs) for mtd in self.findAllWithType(paratype)]

    def invokeFirstWithType(self,paratype:List[object],*args,**kwargs) -> Any:
        return self.findFirstWithType(paratype)(*args,**kwargs)