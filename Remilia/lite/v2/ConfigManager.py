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
            
    def replace_ins(self,path:str):
        self.path=path
        self.model_ins=self.model(File(self.path))
        return self
    
    def replace_model(self,model:KVFileBase):
        self.model=model
        return self
    
class Cate:
    def __call__(self,obj) -> "_getObj":
        self._obj=obj()
        obj=self._obj
        return self
    
    def _withObj(self,obj):
        self.__call__(obj)
        return self
    
    def _handle_temp(self,obj) -> "_getObj":
        self._obj=obj
        return self
    
    def _getObj(self):
        return self._obj
    
    def _modify(self,name,data):
        setattr(self._getObj(),name,data)
        return self
    
    def _toDict(self) -> dict:
        fin={}
        for liter in collect_attr(self._obj):
            for k,v in liter.items():
                if isinstance(v,Cate):
                    fin.update({k:v._toDict()})
                elif isinstance(v,Temp):
                    fin.update({k:v.__to_dict__()})
                else:
                    fin.update({k:v})
        return fin

class Config:
    def __init__(self,setting:ConfigSetting) -> None:
        self._setting=setting
        
    def _withObj(self,obj):
        self.__call__(obj)
        return self
    
    def _push(self,target):
        for liter in collect_attr(target):
            for k,v in liter.items():
                if isinstance(v,Cate):
                    self._setting.model_ins.write(k,v._toDict())
                elif isinstance(v,Temp):
                    self._setting.model_ins.write(k,v.__to_dict__())
                else:
                    #print(v,type(v))
                    self._setting.model_ins.write(k,v)
        return self
    def _get(self,target):
        for k,v in self._setting.model_ins.FileDict.items():
            if isinstance(v,dict):
                if hasattr(target,k) and isinstance(getattr(target,k),Cate):
                    safe_mixin(getattr(target,k),Temp().__to_class__(v))
                    safe_mixin(getattr(target,k)._getObj(),Temp().__to_class__(v))
                elif isinstance(getattr(target,k),Cate):
                    fin=Cate()._handle_temp(Temp().__to_class__(v))
                    safe_mixin(fin,Temp().__to_class__(v))
                    setattr(target,k,fin)
                else:
                    setattr(target,k,v)
            else:
                setattr(target,k,v)
        return self
    def _sync(self):
        try:
            self._get(self._obj)
        except:
            pass
        self._push(self._obj)
        self._get(self._obj)
        return self
    
    def _regenerate(self):
        try:
            self._get(self._obj)
        except:
            pass
        for liter in collect_attr(self._obj):
            for k,v in liter.items():
                if hasattr(self._rawobj,k):
                    setattr(self._rawobj,k,v)
        self._setting.model_ins.File.write("w","{}")
        self._push(self._rawobj)
        return self
    
    def _modify(self,name,obj):
        setattr(self._obj,name,obj)
        return self
    
    def _modify_push(self,name,obj):
        return self._modify(name,obj)._push(self._obj)._get(self._obj)
    
    def __call__(self,obj):
        self._rawobj=obj()
        obj=obj()
        self._obj=obj
        if self._setting.regenerate:
            self._regenerate()
        self._sync()
        setattr(self._obj,"__config__",self)
        return self._obj