class ConfigSetting:
    pass

class Config:
    def __init__(self,setting=None) -> None:
        self.setting=setting

    def __call__(self,obj):
        obj=obj()
        return obj
    
class ConfigVar:
    pass