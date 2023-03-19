import importlib
from Remilia.lite.LiteResource import File, Path




class PluginManager:
    def __init__(self) -> None:
        self.plugins=[]
        
    def load_plugin(self,path:Path):pass
    
    
    
    def __load(self,path:Path):
        if isinstance(path,File):
            path:File
            importlib.import_module(path.name,path.abspath)

class PluginType:pass