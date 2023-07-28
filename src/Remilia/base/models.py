from pydantic import BaseModel
from typing_extensions import Self


class Ruler(BaseModel):
    '''
    self -> Type(Log)
    '''
    level:int=5
    excolor:str="fore.LIGHTGREEN_EX+'[ '+name+' '+time+' '+location+'] '+style.RESET_ALL+text"
    explain:str="'[ '+name+' '+time+' '+location+'] '+text"
    timeformat:str="%H:%M:%S"
    def exgenerate(self,model:str,*color:str) -> Self:
        self.explain=model % tuple(["" for _ in color])
        self.excolor=model % color
        return self
    
class PathTimes(BaseModel):
    createtime:float
    modifytime:float
    accesstime:float
    
class SizeUnits(BaseModel):
    BYTES:str='Bytes'
    K:str='K'
    M:str='M'
    G:str='G'
    
