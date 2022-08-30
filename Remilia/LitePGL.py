class PluginType():
    def __init__(self) -> None:pass

class PluginGroup():
    def __init__(self) -> None:pass


class PluginLoadPoint():
    def __init__(self,name) -> None:
        self.name=name

class PluginLoader():
    def __init__(self,PluginGroup:PluginGroup) -> None:
        self.PluginGroup=PluginGroup
        
    def registPlugin(self,Plugin:PluginType) -> None:
        def warpper(func):
            pass
        return warpper
    