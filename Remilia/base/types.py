class Result:pass
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