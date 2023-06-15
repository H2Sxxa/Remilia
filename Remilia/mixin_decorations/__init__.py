from types import MethodType
from typing import List
from ..base.rtypes import Pair
from ..utils.SignParas import ParaFilter
from .omixin import gc_Mixin
from . import omixin
from abc import abstractmethod

__all__=["omixin"]

class DecorationBase:
    def __call__(self,obj):
        self.obj=obj
        return self
    def withObj(self,obj):
        self.obj=obj
        return self
    
    @abstractmethod
    def warp(self,pair:Pair) -> Pair:
        return Pair(Pair.attr_A,Pair.attr_B)

class ParaHandleBase:
    @abstractmethod
    def warp_para(self,arg):pass

class ParaReplacer(ParaHandleBase):
    def __init__(self,paragen=lambda para:para,condition=lambda para:True) -> None:
        '''
        paragen: method(para) -> replace arg
        condition: wont work until it return True
        '''
        self.paragen=paragen
        self.condition=condition
    
    def warp_para(self, arg):
        if self.condition(arg):
            return self.paragen(arg)
        else:
            return arg

class ParaMixin(ParaHandleBase):
    def __init__(self,mixins:Pair(str,MethodType)=[],condition=lambda para:True,gc=False) -> None:
        '''
        mixins: Pair(method_name,Method)
        condition: wont work until it return True
        '''
        self.mixins=mixins
        self.cd=condition
        self.gc=gc
    def warp_para(self, arg):
        if not self.cd(arg):
            return arg
        new_arg=arg
        for mixin in self.mixins:
            if self.gc:
                gc_Mixin(new_arg,mixin.attr_B,mixin.attr_A)
            else:
                setattr(new_arg,mixin.attr_A,mixin.attr_B)
        return new_arg
    
class ParaHooker(ParaHandleBase):
    def __init__(self,hookname="__getattribute__",bfhooker=lambda *_,**__:None,afhooker=lambda result,*_,**__:result,condition=lambda para:True,gc=False) -> None:
        '''
        ### via mixin inject target , wont work for some buildin method
        hookname: hook target(default is all(maybe) )
        bfhooker: hook before call it
        afhooker: hook after call it
        condition: wont work until it return True
        '''
        self.hn=hookname
        self.bf=bfhooker
        self.af=afhooker
        self.cd=condition
        self.gc=gc
    def warp_para(self,arg):
        if not self.cd(arg):
            return arg
        new_arg=arg
        rawattr=getattr(arg,self.hn)
        def rebuild(*_,**__):
            self.bf(*_,**__)
            result=rawattr(*_,**__)
            return self.af(result,*_,**__)
        if self.gc:
            gc_Mixin(new_arg,rebuild,self.hn)
        else:
            setattr(new_arg,self.hn,rebuild)
        return new_arg
    
class Hooker(DecorationBase):
    def __init__(self,bfhooker=lambda *_,**__:None,afhooker=lambda obj,result,*_,**__:result,parahandle:List[Pair]=[]) -> None:
        '''
        parahandle : [Pair(the index of para,parahandlebase's subclass instance),...]
        bfhooker: hook before call it
        afhooker: hook after call it
        '''
        self.bf=bfhooker
        self.af=afhooker
        self.ph=parahandle
    def warp(self,pair) -> Pair:
        return Pair(pair.attr_A,self.warpper)
    
    @property
    def warpper(self):
        filter=ParaFilter(self.obj)
        filter.load_default()
        filter.fill_none()
        for pair in self.ph:
            filter.index_put(pair.attr_A,pair.attr_B)
        def tmp(*args,**kwargs):
            self.bf(self.obj,*args,**kwargs)
            for arg,index in zip(args,range(0,len(args))):
                default=filter.kwargs[filter.get_index(index).name]
                if isinstance(default,ParaHandleBase):
                    filter.index_put(index,default.warp_para(arg))
                else:
                    filter.index_put(index,arg)
            for k,v in kwargs.items():
                default=filter.get_name(k)
                if isinstance(default,ParaHandleBase):
                    filter.kwargs.update({k:default.warp_para(arg)})
                else:
                    filter.kwargs.update({k:v})
            result=self.obj(**filter.kwargs)
            return self.af(self.obj,result,*args,**kwargs)
        return tmp
        
        
class NameTransform(DecorationBase):
    def __init__(self,real_name) -> None:
        '''
        use to inject self into attr 'real_name'
        PS:Usally in the outside of all decorations
        
        ---
        examples:
        
        ```python
        x=NameTransform("__nameless_var__").withObj(8)
        
        @NameTransform("__nameless_method__")
        def x(self):pass
        
        
        #for some special method,it may be "_cls__method"
        #recommand to use str,instead of a concrete method
        ```
        '''
        if isinstance(real_name,str):
            self.real_name=real_name
        else:
            self.real_name=real_name.__name__
    def __call__(self,obj):
        self.obj=obj
        return self
    
    def withObj(self,obj):
        self.obj=obj
        return self
    
    def warp(self, *_) -> Pair:
        return Pair(self.real_name,self.obj)