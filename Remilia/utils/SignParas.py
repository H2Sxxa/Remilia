from inspect import _empty, signature,Parameter
from types import FunctionType
from typing import List


class ParaFilter:
    def __init__(self,target:FunctionType) -> None:
        self.signargs:List[Parameter]=[]
        self.kwargs={}
        self.target=target
        self.__handle()
        self.load_default()
        
    def __handle(self):
        self.signargs=[signarg for _,signarg in signature(self.target).parameters.items()]
            
    def __check(self,raw,sub):
        return issubclass(sub,raw)
    
    def get_index(self,index):
        return self.signargs[index]
    
    def get_name(self,name) -> Parameter:
        for para in self.signargs:
            if para.name == name:
                return para
            
    def index_put(self,index,value):
        self.update_kwg({self.signargs[index].name:value})
    
    def check_put(self,atype,value):
        self.update_kwg(*[{_.name:value} for _ in self.check_get(atype)])

    def check_put_anno(self,atype):
        self.update_kwg(*[{_.name:_.annotation} for _ in self.check_get(atype)])
        
    def check_put_handle(self,atype,func):
        self.update_kwg(*[{_.name:func(_)} for _ in self.check_get(atype)])

    def check_get(self,atype):
        return [_ for _ in self.signargs if self.__check(atype,_.annotation)]
    
    def load_default(self):
        self.update_kwg(*[{_.name:_.default} for _ in self.signargs if _.default != _empty])
        
    def fill_none(self):
            
        self.update_kwg(*[{_.name:None} for _ in self.signargs if _.default == _empty and _.name not in self.kwargs])
    
    def update_kwg(self,*dicts):
        for d in dicts:
            self.kwargs.update(d)
    
    def __enter__(self):
        self.load_default()
        return self
    
    def __exit__(self,*args,**kwargs):
        self.fill_none()