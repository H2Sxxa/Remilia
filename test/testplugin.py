PluginLoader=self
p2Self=PluginLoader.requestPlugin("p2")

@PluginLoader.registPlugin(PluginLoader.getInterface["LoadPoint1"])
class plugin:
    def __init__(self) -> None:
        global PluginLoader,p2Self
        print("I am p1")
        p2Self.hello("hello")
    def __reference__(self):
        return {
            "pluginid":"p1"
        }