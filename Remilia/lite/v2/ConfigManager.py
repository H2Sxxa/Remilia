from functools import partial
from Remilia.base.files import KVFileBase,File
from Remilia.lite.LiteEvent import BaseEvent,TriggerEvent,SubcribeEvent
from ..LiteData import JsonFile,YamlFile
from ..LiteMixin import safe_mixin
from .utils import collect_attr
class ConfigError(Exception):pass
class ConfigSyncEvent(BaseEvent):pass
class Temp:
    def __to_class__(self,target:dict):
        for k,v in target.items():
            if isinstance(v,dict):
                setattr(self,k,Temp().__to_class__(v))
            else:
                setattr(self,k,v)
        return self
    def __to_dict__(self) -> dict:
        fin={}
        for liter in collect_attr(self):
            for k,v in liter.items():
                if isinstance(v,Temp):
                    fin.update({k:v.__to_dict__()})
                else:
                    fin.update({k:v})
        return fin
    
class ConfigSetting:
    model:KVFileBase=YamlFile
    model_ins:KVFileBase=None
    path:str=None
    regenerate:bool=False
    def __init__(self,**kwargs) -> None:
        '''
        para model:KVFileBase=YamlFile
        para path:File=None
        para regenerate:bool=False
        '''
        for k,v in kwargs.items():
            setattr(self,k,v)
        if not self.path:
            raise ConfigError("can't go on without a path")
        else:
            self.model_ins=self.model(File(self.path))
class Cate:
    def __call__(self,obj) -> Temp:
        self.obj=obj()
        obj=self.obj
        return self
    
    def getObj(self):
        return self.obj
    
    def toDict(self) -> dict:
        fin={}
        for liter in collect_attr(self.obj):
            for k,v in liter.items():
                if isinstance(v,Cate):
                    fin.update({k:v.toDict()})
                else:
                    fin.update({k:v})
        return fin

class Config:
    def __init__(self,setting:ConfigSetting) -> None:
        self.setting=setting
    def push(self,target):
        for liter in collect_attr(target):
            for k,v in liter.items():
                if isinstance(v,Cate):
                    self.setting.model_ins.write(k,v.toDict())
                elif isinstance(v,Temp):
                    self.setting.model_ins.write(k,v.__to_dict__())
                else:
                    self.setting.model_ins.write(k,v)
    def get(self,target):
        for k,v in self.setting.model_ins.FileDict.items():
            if isinstance(v,dict):
                if hasattr(target,k):
                    safe_mixin(getattr(target,k),Temp().__to_class__(v))
            else:
                setattr(target,k,v)
    def sync(self):
        try:
            self.get(self.obj)
        except:
            pass
        self.push(self.obj)
        self.get(self.obj)
        
    def regenerate(self):
        try:
            self.get(self.obj)
        except:
            pass
        for liter in collect_attr(self.obj):
            for k,v in liter.items():
                if hasattr(self.rawobj,k):
                    setattr(self.rawobj,k,v)
        self.setting.model_ins.File.write("w","{}")
        self.push(self.rawobj)
        
    def __call__(self,obj):
        self.rawobj=obj()
        obj=obj()
        self.obj=obj
        if self.setting.regenerate:
            self.regenerate()
        self.sync()
        setattr(self.obj,"__config__",self)
        return obj