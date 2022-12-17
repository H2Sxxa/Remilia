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
            "loadpoint":"point",
            "auther":"",
            "dependences":["pluginid",]
        }
        return reference
    
class PluginGroup():
    def __init__(self) -> None:
        self.PluginList=[]
        
    def addPlugin(self,PluginType:PluginType):
        '''
        dont need to call it manually
        '''
        self.PluginList.append(PluginType)
    
    
class PluginLoadPoint():
    def __init__(self,PluginLoader,name) -> None:
        self.PluginLoader=PluginLoader
        self.name=name
    def run(self):
        '''
        when you have inited the plugin file,use 'PluginLoadPoint.run' to call its __init__ method
        '''
        self.PluginLoader.LoadGroupPluginAtPoint(self)

class PluginLoader():
    def __init__(self,PluginGroup:PluginGroup=PluginGroup()) -> None:
        self.PluginGroup=PluginGroup
        self.PluginInitList=[]
        self.PluginLoadList=[]
        self.PluginList=[]
        self.Interface=self
        
    def setInterface(self,pyClass):
        '''
        set it to globals() can make plugin-dev easier
        '''
        self.Interface=pyClass
        return self.Interface
    
    @property
    def getInterface(self):
        return self.Interface
    
    def initLoadPlugin(self,PluginPath:LiteResource.Path) -> None:
        '''
        call it before the PluginLoadPoint.run()
        '''
        exec(PluginPath.text)
        
    def LoadGroupPluginAtPoint(self,LoadPoint:PluginLoadPoint):
        '''
        dont need to call it manually
        '''
        for PluginType in self.PluginGroup.PluginList:
            if LoadPoint == PluginType.LoadPoint:
                self.LoadPlugin(PluginType)
                
    def LoadPlugin(self,PluginType:PluginType):
        '''
        call the plugintype and return it
        '''
        if PluginType.HasReference and PluginType.__reference__(PluginType)["pluginid"] in self.PluginLoadList:
            return self.searchInPluginList(PluginType.__reference__(PluginType)["pluginid"])
        InClass=PluginType.RegClass(*PluginType.args,**PluginType.kwargs)
        self.PluginList.append(InClass)
        try:
            self.PluginLoadList.append(PluginType.__reference__(PluginType)["pluginid"])
        except:
            print("WARNNING:The %s don't have a __reference__,it may cause some errors" % PluginType.RegClass.__name__)
        return InClass
    
    
    def searchInPluginList(self,pluginid:str):
        '''
        find the plugin with a pluginid,if the obj not in its list,it will return None
        '''
        for plugin in self.PluginList:
            try:
                if plugin.__reference__()["pluginid"] == pluginid:
                    return plugin
            except:
                pass
        return
    
    def requestPlugin(self,pluginid):
        '''
        ask for a plugin to load (if it in the PluginGroup)
        '''
        if pluginid in self.PluginLoadList:
            return self.searchInPluginList(pluginid)
        else:
            for PluginType in self.PluginGroup.PluginList:
                if PluginType.__reference__(PluginType)["pluginid"] == pluginid:
                    return self.LoadPlugin(PluginType)
    
    def registPlugin(self,LoadPoint:PluginLoadPoint,*args,**kwargs):
        '''
        use it with you plugin class,and it will work at initLoadPlugin
        '''
        def warpper(regClass):
            self.PluginGroup.addPlugin(PluginType(LoadPoint,regClass,args,kwargs))
            return regClass
        return warpper