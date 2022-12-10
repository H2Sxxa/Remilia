from typing import Generic, List, TypeVar

class TranslateManager(dict):
    def _switch(self,locations:List[dict],comparedict:dict):
        for location in locations:
            for var in comparedict.keys():
                if var in self.keys() and location.__contains__(var):
                    if id(location[var]) == id(self[var]):
                        location.update({var:comparedict[var]})
    
    def translateAble(self,x:any,varname:str):
        self.update({varname:x})
