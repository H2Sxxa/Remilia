from functools import partial
from Remilia.base.files import KVFileBase,File
from Remilia.lite.LiteEvent import BaseEvent,TriggerEvent,SubcribeEvent
from ..LiteData import JsonFile,YamlFile
from ..LiteMixin import safe_mixin
def collect(target):
    return [{_:getattr(target,_)} for _ in dir(target) if not _.startswith("__") and not _.endswith("_") and not _.startswith("_") and  not _.endswith("_")]
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
        for liter in collect(self):
            for k,v in liter.items():
                if isinstance(v,Temp):
                    fin.update({k:v.__to_dict__()})
                else:
                    fin.update({k:v})
        return fin
    
class ConfigSetting:
    model:KVFileBase=YamlFile
    model_ins:KVFileBase=None
    path:File=None
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
            self.model_ins:KVFileBase=self.model(self.path)
            CSTrigger=TriggerEvent(ConfigSyncEvent)
            setattr(self.model_ins,"_write",CSTrigger(self.model_ins._write))
class Cate:
    def __call__(self,obj):
        self.obj=obj()
        obj=self.obj
        return self
    
    def getObj(self):
        return self.obj
    
    def toDict(self) -> dict:
        fin={}
        for liter in collect(self.obj):
            for k,v in liter.items():
                if isinstance(v,Cate):
                    fin.update({k:v.toDict()})
                else:
                    fin.update({k:v})
        return fin

    def __getattr__(self, name: str) -> None:
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        else:
            if hasattr(self.obj,name):
                return getattr(self.obj,name)

class Config:
    def __init__(self,setting:ConfigSetting) -> None:
        self.setting=setting
    def push(self,target):
        for liter in collect(target):
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
        
    def regenerate(self):
        try:
            self.get(self.obj)
        except:
            pass
        for liter in collect(self.obj):
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