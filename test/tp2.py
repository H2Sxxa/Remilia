PluginLoader=self
@PluginLoader.registPlugin(PluginLoader.getInterface["LoadPoint1"])
class plugin2:
    def __init__(self) -> None:
        print("I am p2")
    
    def hello(self,*args):
        print(*args)

    def __reference__(self):
        return {
            "pluginid":"p2"
        }