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

class Pair:
    def __init__(self,a,b) -> None:
        self.a=a
        self.b=b
    
    def getA(self):
        return self.a
    
    def getB(self):
        return self.b
    
    @property
    def attr_A(self):
        return self.getA()
    
    @property
    def attr_B(self):
        return self.getB()
    
    @staticmethod
    def fromkv(k,v):
        return Pair(k,v)