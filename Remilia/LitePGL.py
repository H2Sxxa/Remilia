
class LitePGL:
    def __init__(self) -> None:
        pass


class Plugin():
    def __init__(self) -> None:pass

class PluginGroup():
    def __init__(self) -> None:pass

class PluginLoader():
    def __init__(self,PluginGroup:PluginGroup) -> None:
        self.PluginGroup=PluginGroup
    def registPlugin(self,Point) -> None:pass