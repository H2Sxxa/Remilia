from os import makedirs
from typing import List
from .utils import collect_attr

class Node:
    def __init__(self,obj) -> None:
        self.obj=obj
    
    def getNodes(self,name):
        res=[]
        for liter in collect_attr(self.obj):
            for k,v in liter.items():
                if isinstance(v,Node):
                    res.append(name+"/"+self.obj.__name__+"/"+k)
                    for i in v.getNodes(name+"/"+self.obj.__name__):
                        res.append(i)
        return res
class DictroyTree:
    gens:List[str]=[]
    def __init__(self,obj) -> None:
        if not isinstance(obj,str):
            root=obj.__name__
        else:
            root=obj
        self.gens.append(root)
        for liter in collect_attr(obj):
            for _,v in liter.items():
                if isinstance(v,Node):
                    self.gens.append(root+"/"+v.obj.__name__)
                    self.gens.extend(v.getNodes(root))
        self.generate()
    def generate(self):
        for i in self.gens:
            try:
                makedirs(i)
            except:pass