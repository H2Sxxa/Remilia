from typing import List
from ....base.rtypes import Pair
from ....utils.SignParas import ParaFilter
from abc import abstractmethod
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
    
    
class ParaHooker:
    def __init__(self,bfhooker=lambda *_,**__:None,afhooker=lambda para,result,*_,**__:result) -> None:
        self._bf=bfhooker
        self._af=afhooker
        self._para=None
    def _setpara(self,x):
        self._para=x
        
    #BUG Can't work
    def __getattr__(self,name):
        self.bf(self.para)
        result=getattr(self._para,name)
        return self.af(self._para,result)
class Hooker(DecorationBase):
    def __init__(self,bfhooker=lambda *_,**__:None,afhooker=lambda obj,result,*_,**__:result,parahooker:List[Pair]=[]) -> None:
        self.bf=bfhooker
        self.af=afhooker
        self.ph=parahooker
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
                if isinstance(default,ParaHooker):
                    filter.index_put(index,default._setpara(arg))
                else:
                    filter.index_put(index,arg)
            for k,v in kwargs.items():
                default=filter.get_name(k)
                if isinstance(default,ParaHooker):
                    filter.kwargs.update({k:default._setpara(v)})
                else:
                    filter.kwargs.update({k:v})
            result=self.obj(**filter.kwargs)
            return self.af(self.obj,result,*args,**kwargs)
        return tmp
        
        
class NameTransform(DecorationBase):
    def __init__(self,real_name) -> None:
        '''
        use to inject self into attr 'real_name'
        
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