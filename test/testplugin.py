from Remilia.LitePGL import PluginType
self=self
@self.registPlugin("loadpoint1")
class plugin(PluginType):
    def __init__(self) -> None:
        print("hello")
    
    def __reference__(self):
        return {
            "pluginid":"1"
        }