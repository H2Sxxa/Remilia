from functools import partial
from Remilia.base.files import KVFileBase,File
from Remilia.lite.LiteEvent import BaseEvent,TriggerEvent
from ..LiteData import JsonFile,YamlFile
class ConfigError(Exception):pass
class ConfigSyncEvent(BaseEvent):pass
class ConfigSetting:
    model:KVFileBase=YamlFile
    model_ins:KVFileBase=None
    path:File=None
    sync:bool=False
    def __init__(self,**kwargs) -> None:
        for k,v in kwargs:
            setattr(self,k,v)
        if not self.path:
            raise ConfigError("can't go on without a path")
        else:
            self.model_ins:KVFileBase=self.model(self.path)
            CSTrigger=TriggerEvent(ConfigSyncEvent)
            setattr(self.model_ins,"_read",CSTrigger(self.model_ins._read))
            
class ConfigBase:
    def __getattr__(self, name: str) -> None:
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

class Config:
    def __init__(self,setting:ConfigSetting) -> None:
        self.setting=setting
    
    def __call__(self,obj):
        obj=obj()
        return obj

class ConfigVar:
    pass