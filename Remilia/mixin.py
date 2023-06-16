import gc
from types import ModuleType
from typing import Any

from .base.rtypes import Pair
from .mixin_decorations.omixin import collect_attr
from .mixin_decorations import DecorationBase
from . import mixin_decorations

__all__=["mixin_decorations"]

class EnumShadow:
    class FOLLOW:pass
class MixinError:pass

class Shadow:
    def __init__(self,default=EnumShadow.FOLLOW) -> None:
        '''
        use to replace target attr (empty default to follow the father)
        
        ---
        examples
        '''
        self.default=default
    def fill(self,attr_name,targetclass):
        if self.default != EnumShadow.FOLLOW or not hasattr(targetclass,attr_name):
            setattr(targetclass,attr_name,self.default)
    def gc_fill(self,attr_name,targetdict:dict):
        if self.default != EnumShadow.FOLLOW or attr_name not in targetdict.keys():
            targetdict[attr_name]=self.default
            

class ModuleMixin:
    def __init__(self,target_module:ModuleType) -> None:
        self.module=target_module
    def __call__(self,canbeinject) -> Any:
        self.module.__dict__.update({canbeinject.__name__:canbeinject})

#TODO Finish it
class Mixin:
    makeAncestor:bool=False
    gc_mixin:bool=False
    def __init__(self,targetClass:object,**kwargs) -> None:
        '''
        a better decoration to help mixin better
        
        ---
        paras:
            gc_mixin:bool=False #use gc to handle some buildin-class (default False)
        examples:
        ```python
        @ClassMixin.Mixin(str,gc_mixin=True)
        class Mixin:
            x=ClassMixin.Shadow(18) #equal to x=18
            
        print("".x)
        
        >>> 18
        ```
        '''
        self.targetClass=targetClass
        for k,v in kwargs.items():
            setattr(self,k,v)
            
    def withObj(self,mixinclass):
        '''
        mannual method to mixin your class
        
        ---
        examples:
        ```python
        class Mixin:
            x=ClassMixin.Shadow(18) #equal to x=18
            
        ClassMixin.Mixin(str,gc_mixin=True).withObj(Mixin)

        print("".x)
        
        >>> 18
        ```
        '''
        self.__call__(mixinclass)
        return self
    
    def __call__(self,mixinclass):
        mixin_map=collect_attr(mixinclass)
        if self.gc_mixin:
            gc_dict=gc.get_referents(self.targetClass.__dict__)[0]
        else:
            gc_dict={}
        for liter in mixin_map:
            for k,v in liter.items():
                while isinstance(v,DecorationBase):
                    pair=v.warp(Pair(k,v))
                    
                    k=pair.attr_A
                    v=pair.attr_B
                    
                if isinstance(v,Shadow):
                    if self.gc_mixin:
                        v.gc_fill(k,gc_dict)
                    else:
                        v.fill(k,self.targetClass)
                else:
                    if self.gc_mixin:
                        gc_dict[k]=v
                    else:
                        setattr(self.targetClass,k,v)