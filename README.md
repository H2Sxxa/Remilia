![https://raw.githubusercontent.com/IAXRetailer/Remilia/main/background.png](https://raw.githubusercontent.com/IAXRetailer/Remilia/main/background.png "PID 100402267")

# Install

```shell
pip install Remilia
```

# Quick start

## LiteLog

```python
from Remilia.LiteLog import LiteLog

Logger=LiteLog(__name__)

Logger.info("hello")

>>>[ INFO | __main__ | 14:58:50 ] hello
```

## LiteEvent

```python
from Remilia.LiteEvent import EventType,EventBus
EventBus=EventBus()

@EventBus.registEvent(EventType("hello"))
def hello():
    print("hello")

@EventBus.registEventTrigger("hello",EventBus.PreEvent)
def beforehello(event:EventType):
    print(f"before the {event.getOBJ().__code__.co_name} event")
    #event.setCancel()
    #print("I cancel the event")
    
@EventBus.registEventTrigger("hello",EventBus.AftEvent)
def beforehello(event:EventType):
    print(f"after the {event.getOBJ().__code__.co_name} event")

hello()

>>>before the hello
>>>hello
>>>after the hello
```

## LiteThread

```python
from Remilia import LiteThread

def hello():
    return "hello"

TVManager=LiteThread.ThreadValueManager()
TestThread=LiteThread.LiteThread(target=hello)
TestThread.start()
print(TVManager.waitResult(TestThread))

>>>hello
```

## LiteMixin

```python
from Remilia import LiteMixin
class A:
    def __init__(self) -> None:
        self.hello()
    def hello(self):
        print("hello")
A()
class A_patch:
    def hello(self):
        print("byebye")

LiteMixin.MixInClass(A,A_patch)
A()


>>>hello
>>>byebye
```

## LitePGL

```python

# main.py
# test
#  - plugin1.py
#  - plugin2.py



#main

from Remilia import LitePGL,LiteResource
PGLoader=LitePGL.PluginLoader()
LoadPoint1=LitePGL.PluginLoadPoint(PGLoader,"loadpoint1")
PGLoader.setInterface(globals())
PGLoader.initLoadPlugin(LiteResource.Path("test/plugin2.py"))
PGLoader.initLoadPlugin(LiteResource.Path("test/plugin1.py"))
LoadPoint1.run()

#test/plugin1.py
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

#test/plugin2.py
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

>>>I am p2
>>>I am p1
>>>hello



```

# There are also some other superising class/method here

# Learn more in our WIKI

## https://github.com/IAXRetailer/Remilia/wiki