from inspect import _empty, signature,Parameter
from types import FunctionType
from typing import List


class ParaFilter:
    def __init__(self,target:FunctionType) -> None:
        self.args:List=[]
        self.signargs:List[Parameter]=[]
        self.kwargs={}
        self.target=target
        self.__handle()
        self.load_default()
        
    def __handle(self):
        self.signargs=[signarg for _,signarg in signature(self.target).parameters.items()]
            
    def __check(self,raw,sub):
        return issubclass(sub,raw)
    
    def check_put(self,atype,value):
        map(self.kwargs.update,[value for _ in self.check_get(atype)])

    def check_put_anno(self,atype):
        map(self.kwargs.update,[_.annotation for _ in self.check_get(atype)])
        
    def check_put_handle(self,atype,func):
        map(self.kwargs.update,[func(_) for _ in self.check_get(atype)])

    def check_get(self,atype):
        return [_ for _ in self.signargs if self.__check(atype,_.annotation)]
    
    def load_default(self):
        map(self.kwargs.update,[{_.name:_.default} for _ in self.signargs if _.default != _empty])
        
    def fill_none(self):
        map(self.kwargs.update,[{_.name:None} for _ in self.signargs if _.default == _empty and _.name not in self.kwargs])
        
    def __enter__(self):
        return self
    
    def __exit__(self,*args,**kwargs):
        self.fill_none()