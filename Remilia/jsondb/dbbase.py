from ..base.types import VarBuilder
class DBVar:
    def initlize(self,db,rootTable):
        self.db=db
        
    
    def sync(self):
        if "db" in dir(self):
            if isinstance(self.db):
                self.uploadtoDB(self.db)
def warp(warpin):
    def inner(*arg,**args):
        print("a var in db")
        return warpin(*arg,**args)
    return inner

VBr=VarBuilder()
DBdict:dict=VBr.new_cls((dict,DBVar,),custom_warp=warp)
DBstr:str=VBr.new_cls((str,DBVar,),custom_warp=warp)
DBint:int=VBr.new_cls((int,DBVar,),custom_warp=warp)
DBfloat:float=VBr.new_cls((float,DBVar,),custom_warp=warp)
#DBbool:bool=VBr.new_cls((bool,DBVar,),custom_warp=warp)
DBlist:list=VBr.new_cls((list,DBVar,),custom_warp=warp)