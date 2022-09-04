from Remilia.LitePGL import PluginLoadPoint, PluginType


PluginLoader=self
@self.registPlugin(self.getInterface["LoadPoint1"])
class plugin(PluginType):
    def __init__(self) -> None:
        global PluginLoader
        PluginLoader.requestPlugin("p2").hello("你好")
    def __reference__(self):
        return {
            "pluginid":"p1"
        }