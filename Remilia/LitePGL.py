from . import LiteResource


class PluginType():
    def __init__(self,LoadPoint,RegClass:object,args,kwargs) -> None:
        self.RegClass=RegClass
        self.HasReference=False
        if "__reference__" in dir(self.RegClass):
            setattr(self,"__reference__",getattr(self.RegClass,"__reference__"))
            self.HasReference=True
        self.args=args
        self.kwargs=kwargs
        self.LoadPoint=LoadPoint
    
    def __reference__(self):
        reference={
            "pluginid":"",
            "license":"",
            "loadpoint":PluginLoadPoint("Point"),
            "auther":"",
            "dependences":["pluginid",]
        }
        return reference
    
class PluginGroup():
    def __init__(self) -> None:
        self.PluginList=[]
        
    def addPlugin(self,PluginType:PluginType):
        self.PluginList.append(PluginType)
    
    
class PluginLoadPoint():
    def __init__(self,PluginLoader,name) -> None:
        self.PluginLoader=PluginLoader
        self.name=name
    def run(self):
        self.PluginLoader.LoadGroupPluginAtPoint(self)

class PluginLoader():
    def __init__(self,PluginGroup:PluginGroup) -> None:
        self.PluginGroup=PluginGroup
        self.PluginInitList=[]
        self.PluginLoadList=[]
        
    def initLoadPlugin(self,PluginPath:LiteResource.Path) -> None:
        exec(PluginPath.text)
    
    def LoadGroupPluginAtPoint(self,LoadPoint:PluginLoadPoint):
        for PluginType in self.PluginGroup.PluginList:
            if LoadPoint.name == PluginType.LoadPoint:
                PluginType.RegClass(*PluginType.args,**PluginType.kwargs)
                try:
                    self.PluginLoadList.append(PluginType.__reference__(PluginType)["pluginid"])
                except:
                    print("WARNNING:The %s don't have a __reference__,it may cause some errors" % PluginType.RegClass.__name__)
                    
    def registPlugin(self,LoadPoint,*args,**kwargs):
        def warpper(regClass):
            self.PluginGroup.addPlugin(PluginType(LoadPoint,regClass,args,kwargs))
            return regClass
        return warpper